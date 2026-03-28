from app.storage.checksum import checksum_bytes


def test_checksum_generation_is_stable():
    assert checksum_bytes(b"nutrideclare") == checksum_bytes(b"nutrideclare")
