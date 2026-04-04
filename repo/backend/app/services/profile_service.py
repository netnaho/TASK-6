import json
import logging

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.models.profile import ParticipantProfile, ParticipantProfileVersion
from app.repositories.profile_repository import ProfileRepository
from app.security.permissions import ensure_profile_owner
from app.services.audit_service import AuditService
from app.services.versioning_service import VersioningService


logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, db):
        self.db = db
        self.repo = ProfileRepository(db)
        self.audit = AuditService(db)

    def get_me(self, user_id):
        profile = self.repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Profile not found.")
        return profile

    def upsert(self, user, payload):
        profile = self.repo.get_by_user_id(user.id)
        profile = self._upsert_profile(user, user, profile, payload)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def import_for_user(self, actor, target_user: User, payload):
        profile = self.repo.get_by_user_id(target_user.id)
        return self._upsert_profile(actor, target_user, profile, payload)

    def _upsert_profile(self, actor, target_user, profile, payload):
        snapshot = payload.model_dump()
        encrypted = json.dumps(snapshot["sensitive"])
        base_payload = {
            "profile_status": payload.profile_status,
            "demographics_json": payload.demographics_json,
            "medical_flags_json": payload.medical_flags_json,
            "activity_json": payload.activity_json,
            "anthropometrics_json": payload.anthropometrics_json,
            "encrypted_payload": encrypted,
        }
        previous_snapshot = None
        if not profile:
            profile = ParticipantProfile(user_id=target_user.id, **base_payload)
            self.db.add(profile)
            self.db.flush()
        else:
            previous_snapshot = self._snapshot(profile)
            for key, value in base_payload.items():
                setattr(profile, key, value)
            self.db.add(profile)
            self.db.flush()
        current_snapshot = self._snapshot(profile)
        current_snapshot["sensitive"] = snapshot["sensitive"]
        version = ParticipantProfileVersion(
            profile_id=profile.id,
            version_number=self.repo.next_version_number(profile.id),
            snapshot_json=current_snapshot,
            change_summary_json=VersioningService.build_change_summary(previous_snapshot, current_snapshot),
            created_by=actor.username,
        )
        self.db.add(version)
        self.db.flush()
        profile.current_version_id = version.id
        self.db.add(profile)
        self.audit.log(actor_user_id=actor.id, action_type="profile_upsert", entity_type="profile", entity_id=str(profile.id), metadata={"version": version.version_number})
        logger.info(
            "Profile upserted",
            extra={"profile_id": str(profile.id), "version": version.version_number, "user_id": str(target_user.id), "actor_user_id": str(actor.id)},
        )
        self.db.flush()
        return profile

    def history(self, user_id):
        profile = self.get_me(user_id)
        return profile.versions

    def get_version(self, user, version_id):
        version = self.repo.get_version(version_id)
        if not version:
            raise NotFoundError("Profile version not found.")
        ensure_profile_owner(user, version.profile)
        return version

    def _snapshot(self, profile):
        return {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "profile_status": profile.profile_status,
            "demographics_json": profile.demographics_json,
            "medical_flags_json": profile.medical_flags_json,
            "activity_json": profile.activity_json,
            "anthropometrics_json": profile.anthropometrics_json,
            "sensitive": json.loads(profile.encrypted_payload) if profile.encrypted_payload else {},
        }
