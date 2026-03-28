from app.models.delivery import DownloadToken
from app.models.scheduler import SchedulerJobRun
from app.utils.datetime import utc_now


def cleanup_expired_download_tokens(db):
    job = SchedulerJobRun(job_name="cleanup_expired_download_tokens", started_at=utc_now(), status="running", details_json={})
    db.add(job)
    db.flush()
    tokens = db.query(DownloadToken).filter(DownloadToken.expires_at < utc_now(), DownloadToken.revoked_at.is_(None)).all()
    for token in tokens:
        token.revoked_at = utc_now()
        db.add(token)
    job.finished_at = utc_now()
    job.status = "success"
    job.details_json = {"revoked_count": len(tokens)}
    db.add(job)
    db.commit()
