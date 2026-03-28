import logging

from app.models.declaration import DeclarationPackage
from app.models.notification import Notification
from app.models.plan import NutritionPlan
from app.models.profile import ParticipantProfile
from app.models.scheduler import SchedulerJobRun
from app.models.settings import SystemSetting
from app.utils.datetime import utc_now

logger = logging.getLogger(__name__)


def rebuild_search_index(db):
    started_at = utc_now()
    job = SchedulerJobRun(job_name="nightly_search_index_rebuild", started_at=started_at, status="running", details_json={})
    db.add(job)
    db.flush()

    snapshot = {
        "generated_at": started_at.isoformat(),
        "declarations": [
            {"id": str(item.id), "package_number": item.package_number, "state": str(item.state)}
            for item in db.query(DeclarationPackage).order_by(DeclarationPackage.created_at.desc()).all()
        ],
        "plans": [
            {"id": str(item.id), "title": item.title, "goal_category": item.goal_category}
            for item in db.query(NutritionPlan).order_by(NutritionPlan.created_at.desc()).all()
        ],
        "profiles": [
            {"id": str(item.id), "user_id": str(item.user_id), "profile_status": item.profile_status}
            for item in db.query(ParticipantProfile).order_by(ParticipantProfile.created_at.desc()).all()
        ],
        "notifications": [
            {"id": str(item.id), "user_id": str(item.user_id), "title": item.title, "type": item.type}
            for item in db.query(Notification).order_by(Notification.created_at.desc()).all()
        ],
    }
    setting = db.query(SystemSetting).filter(SystemSetting.key == "search_index_snapshot").one_or_none()
    if not setting:
        setting = SystemSetting(key="search_index_snapshot", value_json=snapshot, updated_by="scheduler", updated_at=utc_now())
    else:
        setting.value_json = snapshot
        setting.updated_by = "scheduler"
        setting.updated_at = utc_now()
    db.add(setting)

    finished_at = utc_now()
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    job.finished_at = finished_at
    job.status = "success"
    job.details_json = {
        "message": "Search index rebuild completed",
        "duration_ms": duration_ms,
        "declaration_count": len(snapshot["declarations"]),
        "plan_count": len(snapshot["plans"]),
        "profile_count": len(snapshot["profiles"]),
        "notification_count": len(snapshot["notifications"]),
    }
    db.add(job)
    db.commit()
    logger.info("Search index rebuild completed", extra=job.details_json)
