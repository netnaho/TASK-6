from sqlalchemy import func, select

from app.core.constants import ReviewAssignmentStatus
from app.models.declaration import CorrectionRequest, DeclarationPackage, PackageVersion, ReviewAssignment
from app.repositories.base import BaseRepository


class DeclarationRepository(BaseRepository):
    def get(self, package_id):
        return self.scalar_one_or_none(select(DeclarationPackage).where(DeclarationPackage.id == package_id))

    def stmt_for_user(self, user):
        stmt = select(DeclarationPackage)
        if user.role == "participant":
            stmt = stmt.where(DeclarationPackage.participant_id == user.id)
        elif user.role == "reviewer":
            stmt = stmt.join(ReviewAssignment, ReviewAssignment.package_id == DeclarationPackage.id).where(ReviewAssignment.reviewer_id == user.id)
        return stmt.order_by(DeclarationPackage.created_at.desc())

    def list_for_user(self, user):
        return self.list_scalars(self.stmt_for_user(user))

    def next_package_version(self, package_id):
        count = self.db.execute(select(func.count(PackageVersion.id)).where(PackageVersion.package_id == package_id)).scalar_one()
        return int(count) + 1

    def queue_stmt_for_reviewer(self, reviewer_id):
        return (
            select(ReviewAssignment)
            .where(
                ReviewAssignment.reviewer_id == reviewer_id,
                ReviewAssignment.status.in_([ReviewAssignmentStatus.QUEUED, ReviewAssignmentStatus.IN_REVIEW]),
            )
            .order_by(ReviewAssignment.review_due_at.asc())
        )

    def list_queue_for_reviewer(self, reviewer_id):
        return self.list_scalars(self.queue_stmt_for_reviewer(reviewer_id))

    def get_correction(self, correction_id):
        return self.scalar_one_or_none(select(CorrectionRequest).where(CorrectionRequest.id == correction_id))

    def get_active_assignment_for_reviewer(self, package_id, reviewer_id):
        return self.scalar_one_or_none(
            select(ReviewAssignment)
            .where(ReviewAssignment.package_id == package_id, ReviewAssignment.reviewer_id == reviewer_id)
            .order_by(ReviewAssignment.assigned_at.desc())
            .limit(1)
        )
