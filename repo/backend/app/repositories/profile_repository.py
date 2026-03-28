from sqlalchemy import func, select

from app.models.profile import ParticipantProfile, ParticipantProfileVersion
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository):
    def get_by_user_id(self, user_id):
        return self.scalar_one_or_none(select(ParticipantProfile).where(ParticipantProfile.user_id == user_id))

    def get_version(self, version_id):
        return self.scalar_one_or_none(select(ParticipantProfileVersion).where(ParticipantProfileVersion.id == version_id))

    def next_version_number(self, profile_id) -> int:
        count = self.db.execute(select(func.count(ParticipantProfileVersion.id)).where(ParticipantProfileVersion.profile_id == profile_id)).scalar_one()
        return int(count) + 1
