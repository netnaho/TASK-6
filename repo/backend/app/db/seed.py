import json

from sqlalchemy import text

from app.core.constants import DeclarationState, NotificationSeverity, NotificationType, ReviewAssignmentStatus, Role, UserStatus
from app.models.auth import PasswordHistory
from app.models.declaration import DeclarationPackage, DeclarationStateHistory, PackageVersion, ReviewAssignment
from app.models.notification import Notification
from app.models.plan import NutritionPlan, NutritionPlanVersion, PlanPhase
from app.models.profile import ParticipantProfile, ParticipantProfileVersion
from app.models.settings import SystemSetting
from app.models.user import NotificationPreference, User
from app.security.encryption import EncryptionService
from app.security.passwords import hash_password
from app.utils.datetime import add_hours, utc_now


def _ensure_audit_immutability_guards(db) -> None:
    db.execute(
        text(
            """
            CREATE OR REPLACE FUNCTION prevent_audit_log_delete()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'audit_logs is append-only and cannot be deleted';
            END;
            $$;
            """
        )
    )
    db.execute(
        text(
            """
            CREATE OR REPLACE FUNCTION restrict_audit_log_update()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                IF (to_jsonb(NEW) - 'archived_at') IS DISTINCT FROM (to_jsonb(OLD) - 'archived_at') THEN
                    RAISE EXCEPTION 'audit_logs is immutable; only archived_at may be updated';
                END IF;
                RETURN NEW;
            END;
            $$;
            """
        )
    )
    db.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_prevent_audit_log_delete') THEN
                    CREATE TRIGGER trg_prevent_audit_log_delete
                    BEFORE DELETE ON audit_logs
                    FOR EACH ROW
                    EXECUTE FUNCTION prevent_audit_log_delete();
                END IF;
            END;
            $$;
            """
        )
    )
    db.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_restrict_audit_log_update') THEN
                    CREATE TRIGGER trg_restrict_audit_log_update
                    BEFORE UPDATE ON audit_logs
                    FOR EACH ROW
                    EXECUTE FUNCTION restrict_audit_log_update();
                END IF;
            END;
            $$;
            """
        )
    )


def seed_demo_data(db):
    if db.query(User).count() > 0:
        return
    EncryptionService().ensure_pgcrypto_extension(db)
    _ensure_audit_immutability_guards(db)

    participant_password = hash_password("Participant#2026")
    reviewer_password = hash_password("Reviewer#2026")
    admin_password = hash_password("Admin#2026Secure")

    participant = User(username="participant_demo", full_name="Pat Participant", email_optional="participant@example.local", role=Role.PARTICIPANT, status=UserStatus.ACTIVE, password_hash=participant_password, is_active=True)
    reviewer = User(username="reviewer_demo", full_name="Riley Reviewer", email_optional="reviewer@example.local", role=Role.REVIEWER, status=UserStatus.ACTIVE, password_hash=reviewer_password, is_active=True)
    admin = User(username="admin_demo", full_name="Avery Admin", email_optional="admin@example.local", role=Role.ADMINISTRATOR, status=UserStatus.ACTIVE, password_hash=admin_password, is_active=True)
    db.add_all([participant, reviewer, admin])
    db.flush()

    for user, password_hash in [(participant, participant_password), (reviewer, reviewer_password), (admin, admin_password)]:
        db.add(NotificationPreference(user_id=user.id))
        db.add(PasswordHistory(user_id=user.id, password_hash=password_hash, created_at=utc_now()))

    profile = ParticipantProfile(
        user_id=participant.id,
        profile_status="complete",
        demographics_json={"age": 34, "gender": "female"},
        medical_flags_json={"has_allergies": True},
        activity_json={"activity_level": "moderate"},
        anthropometrics_json={"height_cm": 170, "weight_kg": 68},
        encrypted_payload=json.dumps({"allergy_detail": "Tree nuts", "clinician_notes": "Monitor iron intake"}),
    )
    db.add(profile)
    db.flush()
    profile_version = ParticipantProfileVersion(profile_id=profile.id, version_number=1, snapshot_json={"profile_status": "complete"}, change_summary_json=[], created_by=participant.username)
    db.add(profile_version)
    db.flush()
    profile.current_version_id = profile_version.id

    plan = NutritionPlan(participant_id=participant.id, profile_id=profile.id, title="12 Week Energy Balance", duration_weeks=12, goal_category="weight_management", status="draft")
    db.add(plan)
    db.flush()
    plan_version = NutritionPlanVersion(plan_id=plan.id, version_number=1, summary="Foundational energy balance program", phase_count=3, snapshot_json={"title": plan.title}, change_summary_json=[], created_by=participant.username)
    db.add(plan_version)
    db.flush()
    plan.current_version_id = plan_version.id
    for phase_number in range(1, 4):
        db.add(PlanPhase(plan_version_id=plan_version.id, phase_number=phase_number, week_start=(phase_number - 1) * 4 + 1, week_end=phase_number * 4, objective=f"Phase {phase_number} objective", calorie_target=2000 - phase_number * 50, macro_targets_json={"protein": 120}, habits_json=["hydrate"], success_metrics_json=["weekly consistency"]))

    package = DeclarationPackage(
        package_number="PKG-DEMO-0001",
        participant_id=participant.id,
        profile_id=profile.id,
        plan_id=plan.id,
        current_profile_version_id=profile_version.id,
        current_plan_version_id=plan_version.id,
        state=DeclarationState.SUBMITTED,
        submitted_at=utc_now(),
        review_due_at=add_hours(72),
    )
    db.add(package)
    db.flush()
    assignment = ReviewAssignment(
        package_id=package.id,
        reviewer_id=reviewer.id,
        assigned_at=utc_now(),
        review_due_at=package.review_due_at,
        priority="normal",
        status=ReviewAssignmentStatus.QUEUED,
    )
    db.add(assignment)
    db.flush()
    package.current_review_assignment_id = assignment.id
    db.add(DeclarationStateHistory(package_id=package.id, from_state=None, to_state=DeclarationState.SUBMITTED, reason_code=None, reason_text=None, changed_by=participant.username, changed_at=utc_now()))
    db.add(PackageVersion(package_id=package.id, version_number=1, state=DeclarationState.SUBMITTED, profile_version_id=profile_version.id, plan_version_id=plan_version.id, snapshot_json={"state": "submitted"}, change_summary_json=[], created_by=participant.username))

    db.add(Notification(user_id=participant.id, type=NotificationType.MANDATORY_COMPLIANCE_ALERT, severity=NotificationSeverity.CRITICAL, title="Compliance review pending", message="Your declaration package requires review completion.", link_path=f"/app/participant/declarations/{package.id}", is_muted_snapshot=False))
    for key, value in {
        "enable_local_captcha": True,
        "default_download_expiry_hours": 72,
        "notifications_retention_days": 90,
        "review_due_hours": 72,
        "audit_retention_years": 7,
    }.items():
        db.add(SystemSetting(key=key, value_json={"value": value}, updated_by="system", updated_at=utc_now()))
    db.commit()
