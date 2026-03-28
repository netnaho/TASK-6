import os
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.storage.checksum import checksum_bytes


class FileManager:
    def __init__(self) -> None:
        self.root = get_settings().storage_path
        self.root.mkdir(parents=True, exist_ok=True)

    def ensure_dirs(self) -> None:
        for child in ["deliveries", "exports", "imports", "receipts", "bulk", "archives"]:
            (self.root / child).mkdir(parents=True, exist_ok=True)

    def write_bytes(self, folder: str, filename: str, content: bytes) -> tuple[str, int, str]:
        ext = Path(filename).suffix
        path = self.root / folder / f"{uuid.uuid4()}{ext}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path), len(content), checksum_bytes(content)

    def read_bytes(self, path: str) -> bytes:
        return Path(path).read_bytes()

    def exists(self, path: str) -> bool:
        return os.path.exists(path)
