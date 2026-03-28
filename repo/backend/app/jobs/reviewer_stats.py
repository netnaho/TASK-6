import logging
from collections import defaultdict

from app.models.declaration import CorrectionRequest, ReviewAssignment
from app.models.scheduler import SchedulerJobRun
from app.models.settings import SystemSetting
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.datetime import utc_now

logger = logging.getLogger(__name__)


def _emit_deadline_warnings(db) -> dict[str, int]:
    notifications = NotificationService(db)
    now = utc_now()
    warning_horizon_hours = 24
    reviewer_warnings = 0
    participant_warnings = 0

    pending_assignments = db.query(ReviewAssignment).filter(ReviewAssignment.status.in_(["queued", "in_review"])).all()
    for assignment in pending_assignments:
        hours_remaining = (assignment.review_due_at - now).total_seconds() / 3600
        if 0 <= hours_remaining <= warning_horizon_hours:
            notifications.create_deadline_warning(
                user_id=assignment.reviewer_id,
                title="Review deadline approaching",
                message=f"Review for package {assignment.package.package_number} is due by {assignment.review_due_at.isoformat()}.",
                link_path=f"/app/reviewer/packages/{assignment.package_id}",
            )
            reviewer_warnings += 1

    open_corrections = db.query(CorrectionRequest).filter(CorrectionRequest.status.in_(["open", "acknowledged"])).all()
    for correction in open_corrections:
        hours_remaining = (correction.response_due_at - now).total_seconds() / 3600
        if 0 <= hours_remaining <= warning_horizon_hours:
            notifications.create_deadline_warning(
                user_id=correction.package.participant_id,
                title="Correction deadline approaching",
                message=f"Correction response for package {correction.package.package_number} is due by {correction.response_due_at.isoformat()}.",
                link_path=f"/app/participant/declarations/{correction.package_id}",
            )
            participant_warnings += 1

    return {
        "reviewer_deadline_warning_attempts": reviewer_warnings,
        "participant_deadline_warning_attempts": participant_warnings,
    }


def refresh_reviewer_stats(db):
    started_at = utc_now()
    job = SchedulerJobRun(job_name="hourly_reviewer_stats_refresh", started_at=started_at, status="running", details_json={})
    db.add(job)
    db.flush()

    stats: dict[str, dict] = defaultdict(dict)
    reviewers = db.query(User).filter(User.role == "reviewer", User.is_active.is_(True)).all()
    assignments = db.query(ReviewAssignment).order_by(ReviewAssignment.assigned_at.desc()).all()
    for reviewer in reviewers:
        reviewer_assignments = [item for item in assignments if str(item.reviewer_id) == str(reviewer.id)]
        pending = [item for item in reviewer_assignments if str(item.status) in {"queued", "in_review"}]
        overdue = [item for item in pending if item.review_due_at < utc_now()]
        completed = [item for item in reviewer_assignments if str(item.status) == "completed"]
        avg_review_seconds = 0
        if completed:
            avg_review_seconds = int(sum((item.updated_at - item.assigned_at).total_seconds() for item in completed) / len(completed))
        stats[str(reviewer.id)] = {
            "reviewer_username": reviewer.username,
            "pending_reviews": len(pending),
            "overdue_reviews": len(overdue),
            "average_review_seconds": avg_review_seconds,
        }

    setting = db.query(SystemSetting).filter(SystemSetting.key == "reviewer_workload_stats").one_or_none()
    payload = {"generated_at": started_at.isoformat(), "reviewers": stats}
    if not setting:
        setting = SystemSetting(key="reviewer_workload_stats", value_json=payload, updated_by="scheduler", updated_at=utc_now())
    else:
        setting.value_json = payload
        setting.updated_by = "scheduler"
        setting.updated_at = utc_now()
    db.add(setting)

    finished_at = utc_now()
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    total_pending = sum(item["pending_reviews"] for item in stats.values())
    total_overdue = sum(item["overdue_reviews"] for item in stats.values())
    warning_counts = _emit_deadline_warnings(db)
    job.finished_at = finished_at
    job.status = "success"
    job.details_json = {
        "duration_ms": duration_ms,
        "reviewer_count": len(reviewers),
        "total_pending_reviews": total_pending,
        "total_overdue_reviews": total_overdue,
        **warning_counts,
    }
    db.add(job)
    db.commit()
    logger.info("Reviewer workload statistics refreshed", extra=job.details_json)
