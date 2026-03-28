from app.core.exceptions import NotFoundError, ValidationError
from app.models.plan import NutritionPlan, NutritionPlanVersion, PlanPhase
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.security.permissions import ensure_plan_owner
from app.services.audit_service import AuditService
from app.services.versioning_service import VersioningService


class PlanService:
    def __init__(self, db):
        self.db = db
        self.repo = PlanRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.audit = AuditService(db)

    def create(self, user, payload):
        profile = self.profile_repo.get_by_user_id(user.id)
        if not profile:
            raise ValidationError("A health profile is required before creating a plan.")
        plan = NutritionPlan(
            participant_id=user.id,
            profile_id=profile.id,
            title=payload.title,
            duration_weeks=payload.duration_weeks,
            goal_category=payload.goal_category,
            status="draft",
        )
        self.db.add(plan)
        self.db.flush()
        self._create_version(plan, payload, user.username, None)
        self.audit.log(actor_user_id=user.id, action_type="plan_create", entity_type="plan", entity_id=str(plan.id), metadata={})
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, user, plan_id, payload):
        plan = self.repo.get(plan_id)
        if not plan:
            raise NotFoundError("Plan not found.")
        ensure_plan_owner(user, plan)
        previous = plan.versions[-1].snapshot_json if plan.versions else None
        plan.title = payload.title
        plan.duration_weeks = payload.duration_weeks
        plan.goal_category = payload.goal_category
        self.db.add(plan)
        self.db.flush()
        self._create_version(plan, payload, user.username, previous)
        self.audit.log(actor_user_id=user.id, action_type="plan_update", entity_type="plan", entity_id=str(plan.id), metadata={})
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def _create_version(self, plan, payload, created_by: str, previous):
        snapshot = payload.model_dump()
        version = NutritionPlanVersion(
            plan_id=plan.id,
            version_number=self.repo.next_version_number(plan.id),
            summary=payload.summary,
            phase_count=len(payload.phases),
            snapshot_json=snapshot,
            change_summary_json=VersioningService.build_change_summary(previous, snapshot),
            created_by=created_by,
        )
        self.db.add(version)
        self.db.flush()
        for phase in payload.phases:
            self.db.add(PlanPhase(plan_version_id=version.id, **phase.model_dump()))
        plan.current_version_id = version.id
        self.db.add(plan)

    def get(self, plan_id):
        plan = self.repo.get(plan_id)
        if not plan:
            raise NotFoundError("Plan not found.")
        return plan

    def list_for_user(self, user):
        return self.repo.list_for_participant(user.id)

    def versions(self, user, plan_id):
        plan = self.get(plan_id)
        ensure_plan_owner(user, plan)
        return plan.versions

    def get_version(self, user, version_id):
        version = self.repo.get_version(version_id)
        if not version:
            raise NotFoundError("Plan version not found.")
        ensure_plan_owner(user, version.plan)
        return version
