from app.models.import_export import FieldMapping, MaskingPolicy
from app.services.import_export_service import ImportExportService


def test_export_masking_applies_policy(db_session):
    policy = MaskingPolicy(name="Mask IDs", entity_type="declaration", rules_json={"mask_fields": ["participant_id"]}, is_default=False)
    db_session.add(policy)
    db_session.commit()
    rows = [{"participant_id": "abc", "state": "submitted"}]
    masked = ImportExportService(db_session).apply_masking(rows, policy.id)
    assert masked[0]["participant_id"] == "***MASKED***"


def test_field_mapping_applies_to_import_and_export_rows(db_session):
    mapping = FieldMapping(name="Declaration map", entity_type="declaration", format="csv", mapping_json={"package_number": "Package Number", "state": "State"}, is_active=True)
    db_session.add(mapping)
    db_session.commit()
    service = ImportExportService(db_session)

    imported = service.apply_import_mapping([{"Package Number": "PKG-1", "State": "submitted"}], mapping.id)
    assert imported[0]["package_number"] == "PKG-1"
    assert imported[0]["state"] == "submitted"

    exported = service.apply_export_mapping([{"package_number": "PKG-1", "state": "submitted"}], mapping.id)
    assert exported[0]["Package Number"] == "PKG-1"
    assert exported[0]["State"] == "submitted"
