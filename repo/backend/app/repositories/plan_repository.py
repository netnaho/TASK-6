from sqlalchemy import func, select

from app.models.plan import NutritionPlan, NutritionPlanVersion
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository):
    def get(self, plan_id):
        return self.scalar_one_or_none(select(NutritionPlan).where(NutritionPlan.id == plan_id))

    def list_for_participant(self, participant_id):
        return self.list_scalars(select(NutritionPlan).where(NutritionPlan.participant_id == participant_id).order_by(NutritionPlan.created_at.desc()))

    def get_version(self, version_id):
        return self.scalar_one_or_none(select(NutritionPlanVersion).where(NutritionPlanVersion.id == version_id))

    def next_version_number(self, plan_id):
        count = self.db.execute(select(func.count(NutritionPlanVersion.id)).where(NutritionPlanVersion.plan_id == plan_id)).scalar_one()
        return int(count) + 1
