from sqlalchemy import select

from app.models.delivery import AcceptanceConfirmation, DeliveryFile, DownloadToken
from app.repositories.base import BaseRepository


class DeliveryRepository(BaseRepository):
    def list_files(self, package_id):
        return self.list_scalars(select(DeliveryFile).where(DeliveryFile.package_id == package_id).order_by(DeliveryFile.created_at.desc()))

    def get_file(self, file_id):
        return self.scalar_one_or_none(select(DeliveryFile).where(DeliveryFile.id == file_id))

    def get_download_token(self, token_hash):
        return self.scalar_one_or_none(select(DownloadToken).where(DownloadToken.token_hash == token_hash))

    def list_acceptance(self, package_id):
        return self.list_scalars(select(AcceptanceConfirmation).where(AcceptanceConfirmation.package_id == package_id).order_by(AcceptanceConfirmation.confirmed_at.desc()))
