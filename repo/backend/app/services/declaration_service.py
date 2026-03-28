import logging
import uuid

from app.core.config import get_settings
from app.core.constants import CorrectionStatus, DeclarationState, NotificationSeverity, NotificationType, ReviewAssignmentStatus, Role
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.declaration import CorrectionRequest, DeclarationPackage, DeclarationStateHistory, PackageVersion, ReviewAssignment
from app.models.user import User
from app.repositories.declaration_repository import DeclarationRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.runtime_settings_service import RuntimeSettingsService
from app.services.versioning_service import VersioningService
from app.security.permissions import ensure_package_owner
from app.utils.datetime import add_hours, utc_now


logger = logging.getLogger(__name__)


LEGAL_TRANSITIONS = {
    DeclarationState.DRAFT: {DeclarationState.SUBMITTED, DeclarationState.VOIDED},
    DeclarationState.SUBMITTED: {DeclarationState.WITHDRAWN, DeclarationState.CORRECTED, DeclarationState.VOIDED},
    DeclarationState.WITHDRAWN: {DeclarationState.DRAFT, DeclarationState.VOIDED},
    DeclarationState.CORRECTED: {DeclarationState.SUBMITTED, DeclarationState.VOIDED},
    DeclarationState.VOIDED: set(),
}


class DeclarationService:
    def __init__(self, db):
        self.db = db
        self.repo = DeclarationRepository(db)
        self.plan_repo = PlanRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.settings = get_settings()
        self.runtime_settings = RuntimeSettingsService(db)

    def _review_due_hours(self) -> int:
        value = self.runtime_settings.get("review_due_hours", self.settings.review_due_hours)
        if isinstance(value, bool):
            return int(self.settings.review_due_hours)
        if isinstance(value, (int, float, str)):
            return int(value)
        return int(self.settings.review_due_hours)

    def create(self, user, profile_id, plan_id):
        profile = self.profile_repo.get_by_user_id(user.id)
        plan = self.plan_repo.get(plan_id)
        if not profile or str(profile.id) != str(profile_id):
            raise ValidationError("Profile mismatch.")
        if not plan or str(plan.profile_id) != str(profile_id):
            raise ValidationError("Plan mismatch.")
        package = DeclarationPackage(
            package_number=f"PKG-{utc_now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}",
            participant_id=user.id,
            profile_id=profile_id,
            plan_id=plan_id,
            current_profile_version_id=profile.current_version_id,
            current_plan_version_id=plan.current_version_id,
            state=DeclarationState.DRAFT,
        )
        self.db.add(package)
        self.db.flush()
        self._write_version(package, user.username, None)
        self._write_state_history(package, None, DeclarationState.DRAFT, user.username, None, None)
        self.audit.log(actor_user_id=user.id, action_type="declaration_create", entity_type="declaration", entity_id=str(package.id), metadata={})
        self.db.commit()
        self.db.refresh(package)
        return package

    def transition(self, user, package_id, to_state: DeclarationState, reason_code: str | None = None, reason_text: str | None = None):
        package = self.get(package_id)
        assigned_reviewer = None
        if to_state not in LEGAL_TRANSITIONS[package.state]:
            raise ConflictError(f"Illegal declaration transition from {package.state} to {to_state}.")
        if to_state == DeclarationState.SUBMITTED and package.state == DeclarationState.DRAFT:
            profile = self.profile_repo.get_by_user_id(package.participant_id)
            plan = self.plan_repo.get(package.plan_id)
            if not profile or not profile.current_version_id or not plan or not plan.current_version_id:
                raise ValidationError("Package requires current profile and plan versions before submission.")
            reviewer = self.db.query(User).filter(User.role == Role.REVIEWER, User.is_active.is_(True)).order_by(User.created_at.asc()).first()
            if not reviewer:
                raise ValidationError("No active reviewer is available for assignment.")
            assigned_reviewer = reviewer
            package.current_profile_version_id = profile.current_version_id
            package.current_plan_version_id = plan.current_version_id
            package.submitted_at = utc_now()
            assignment = ReviewAssignment(
                package_id=package.id,
                reviewer_id=reviewer.id,
                assigned_at=utc_now(),
                review_due_at=add_hours(self._review_due_hours()),
                priority="normal",
                status=ReviewAssignmentStatus.QUEUED,
            )
            self.db.add(assignment)
            self.db.flush()
            package.current_review_assignment_id = assignment.id
            package.review_due_at = assignment.review_due_at
        if to_state == DeclarationState.WITHDRAWN:
            package.withdrawn_at = utc_now()
        if to_state == DeclarationState.VOIDED:
            if not reason_text:
                raise ValidationError("Void reason is required.")
            package.voided_at = utc_now()
        old_state = package.state
        package.state = to_state
        self.db.add(package)
        self._write_state_history(package, old_state, to_state, user.username, reason_code, reason_text)
        self._write_version(package, user.username, old_state)
        self.notifications.create(
            user_id=package.participant_id,
            notification_type=NotificationType.STATUS_CHANGE,
            severity=NotificationSeverity.INFO,
            title="Declaration status changed",
            message=f"Package {package.package_number} moved to {to_state}.",
            link_path=f"/app/participant/declarations/{package.id}",
        )
        if assigned_reviewer and package.review_due_at:
            hours_remaining = (package.review_due_at - utc_now()).total_seconds() / 3600
            if hours_remaining <= 24:
                self.notifications.create_deadline_warning(
                    user_id=assigned_reviewer.id,
                    title="Review deadline approaching",
                    message=f"Review for package {package.package_number} is due by {package.review_due_at.isoformat()}.",
                    link_path=f"/app/reviewer/packages/{package.id}",
                )
        self.audit.log(actor_user_id=user.id, action_type="declaration_transition", entity_type="declaration", entity_id=str(package.id), metadata={"from": old_state, "to": to_state})
        logger.info(
            "Declaration state transition",
            extra={"package_id": str(package.id), "from_state": str(old_state), "to_state": str(to_state)},
        )
        self.db.commit()
        self.db.refresh(package)
        return package

    def request_correction(self, reviewer, package_id, payload):
        package = self.get(package_id)
        if package.state != DeclarationState.SUBMITTED:
            raise ConflictError("Corrections can only be requested from submitted packages.")
        assignment = self.repo.get_active_assignment_for_reviewer(package.id, reviewer.id)
        if not assignment:
            assignment = ReviewAssignment(
                package_id=package.id,
                reviewer_id=reviewer.id,
                assigned_at=utc_now(),
                review_due_at=package.review_due_at or add_hours(self._review_due_hours()),
                priority="normal",
                status=ReviewAssignmentStatus.IN_REVIEW,
            )
            self.db.add(assignment)
            self.db.flush()
        else:
            assignment.status = ReviewAssignmentStatus.IN_REVIEW
            self.db.add(assignment)
        correction = CorrectionRequest(
            package_id=package.id,
            review_assignment_id=assignment.id,
            requested_by=reviewer.id,
            requested_at=utc_now(),
            response_due_at=add_hours(payload.response_due_hours),
            status=CorrectionStatus.OPEN,
            sections_json=payload.sections_json,
            overall_message=payload.overall_message,
        )
        self.db.add(correction)
        self.db.flush()
        self.transition(reviewer, package_id, DeclarationState.CORRECTED, reason_code="correction_requested", reason_text=payload.overall_message)
        self.notifications.create(
            user_id=package.participant_id,
            notification_type=NotificationType.REVIEW_REQUEST,
            severity=NotificationSeverity.WARNING,
            title="Correction required",
            message=payload.overall_message,
            link_path=f"/app/participant/declarations/{package.id}",
        )
        mention_texts = [payload.overall_message]
        for section in payload.sections_json:
            mention_texts.extend(str(value) for value in section.values() if isinstance(value, str))
        self.notifications.create_mentions(
            source_type="correction_request",
            source_id=correction.id,
            mentioned_by=reviewer,
            texts=mention_texts,
            link_path=f"/app/participant/declarations/{package.id}",
        )
        if correction.response_due_at:
            hours_remaining = (correction.response_due_at - utc_now()).total_seconds() / 3600
            if hours_remaining <= 24:
                self.notifications.create_deadline_warning(
                    user_id=package.participant_id,
                    title="Correction deadline approaching",
                    message=f"Correction response for package {package.package_number} is due by {correction.response_due_at.isoformat()}.",
                    link_path=f"/app/participant/declarations/{package.id}",
                )
        logger.info(
            "Correction requested",
            extra={
                "package_id": str(package.id),
                "correction_id": str(correction.id),
                "review_assignment_id": str(assignment.id),
            },
        )
        self.db.commit()
        return correction

    def complete_review(self, reviewer, package_id, note: str | None = None):
        package = self.get(package_id)
        assignment = self.repo.get_active_assignment_for_reviewer(package.id, reviewer.id)
        if not assignment:
            raise NotFoundError("Review assignment not found.")
        if assignment.status == ReviewAssignmentStatus.COMPLETED:
            raise ConflictError("Review assignment is already completed.")
        assignment.status = ReviewAssignmentStatus.COMPLETED
        self.db.add(assignment)

        if package.current_review_assignment_id == assignment.id:
            package.review_due_at = None
            self.db.add(package)

        for correction in package.correction_requests:
            if correction.status in {CorrectionStatus.OPEN, CorrectionStatus.ACKNOWLEDGED, CorrectionStatus.RESUBMITTED}:
                correction.status = CorrectionStatus.CLOSED
                self.db.add(correction)

        self.notifications.create(
            user_id=package.participant_id,
            notification_type=NotificationType.STATUS_CHANGE,
            severity=NotificationSeverity.INFO,
            title="Review completed",
            message=note or f"Review completed for package {package.package_number}.",
            link_path=f"/app/participant/declarations/{package.id}",
        )
        self.audit.log(
            actor_user_id=reviewer.id,
            action_type="review_completed",
            entity_type="review_assignment",
            entity_id=str(assignment.id),
            metadata={"package_id": str(package.id), "note": note},
        )
        logger.info(
            "Review completed",
            extra={"assignment_id": str(assignment.id), "package_id": str(package.id), "reviewer_id": str(reviewer.id)},
        )
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def acknowledge_correction(self, user, package_id, correction_id):
        correction = self.repo.get_correction(correction_id)
        if not correction or str(correction.package_id) != str(package_id):
            raise NotFoundError("Correction request not found.")
        package = self.get(package_id)
        ensure_package_owner(user, package)
        if correction.response_due_at < utc_now():
            raise ConflictError("Correction response deadline has passed.")
        correction.status = CorrectionStatus.ACKNOWLEDGED
        correction.participant_acknowledged_at = utc_now()
        self.db.add(correction)
        self.audit.log(actor_user_id=user.id, action_type="correction_acknowledged", entity_type="correction_request", entity_id=str(correction.id), metadata={})
        self.db.commit()
        return correction

    def resubmit_correction(self, user, package_id, correction_id, reason_text: str | None):
        correction = self.repo.get_correction(correction_id)
        if not correction or str(correction.package_id) != str(package_id):
            raise NotFoundError("Correction request not found.")
        package = self.get(package_id)
        ensure_package_owner(user, package)
        if correction.response_due_at < utc_now():
            raise ConflictError("Correction response deadline has passed.")
        correction.status = CorrectionStatus.RESUBMITTED
        correction.participant_resubmitted_at = utc_now()
        self.db.add(correction)
        package = self.transition(user, package_id, DeclarationState.SUBMITTED, reason_code="resubmission", reason_text=reason_text)
        return package

    def list_for_user(self, user):
        return self.repo.list_for_user(user)

    def get(self, package_id):
        package = self.repo.get(package_id)
        if not package:
            raise NotFoundError("Declaration package not found.")
        return package

    def queue(self, reviewer_id):
        return self.repo.list_queue_for_reviewer(reviewer_id)

    def _write_state_history(self, package, from_state, to_state, username, reason_code, reason_text):
        self.db.add(DeclarationStateHistory(
            package_id=package.id,
            from_state=from_state,
            to_state=to_state,
            reason_code=reason_code,
            reason_text=reason_text,
            changed_by=username,
            changed_at=utc_now(),
        ))

    def _write_version(self, package, username, previous_state):
        previous_snapshot = package.versions[-1].snapshot_json if package.versions else None
        snapshot = {
            "package_number": package.package_number,
            "profile_version_id": str(package.current_profile_version_id) if package.current_profile_version_id else None,
            "plan_version_id": str(package.current_plan_version_id) if package.current_plan_version_id else None,
            "state": package.state,
        }
        self.db.add(PackageVersion(
            package_id=package.id,
            version_number=self.repo.next_package_version(package.id),
            state=package.state,
            profile_version_id=package.current_profile_version_id,
            plan_version_id=package.current_plan_version_id,
            snapshot_json=snapshot,
            change_summary_json=VersioningService.build_change_summary(previous_snapshot, snapshot),
            created_by=username,
        ))
