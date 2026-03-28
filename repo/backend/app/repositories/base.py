from sqlalchemy import select


class BaseRepository:
    def __init__(self, db):
        self.db = db

    def add(self, instance):
        self.db.add(instance)
        return instance

    def scalar_one_or_none(self, stmt):
        return self.db.execute(stmt).scalar_one_or_none()

    def list_scalars(self, stmt):
        return list(self.db.execute(stmt).scalars().all())
