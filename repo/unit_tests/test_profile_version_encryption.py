from sqlalchemy import text

from app.services.profile_service import ProfileService
from app.schemas.profiles import ProfileUpsertRequest, SensitiveProfilePayload
from app.repositories.user_repository import UserRepository


def test_profile_version_snapshots_are_not_stored_in_plaintext(db_session):
    participant = UserRepository(db_session).get_by_username("participant_demo")
    payload = ProfileUpsertRequest(
        profile_status="complete",
        demographics_json={"age": 35},
        medical_flags_json={"has_allergies": True},
        activity_json={"activity_level": "moderate"},
        anthropometrics_json={"height_cm": 170, "weight_kg": 68},
        sensitive=SensitiveProfilePayload(allergy_detail="Sesame", clinician_notes="Confidential note"),
    )

    profile = ProfileService(db_session).upsert(participant, payload)
    version_id = str(profile.current_version_id)

    row = db_session.execute(text("SELECT snapshot_json, change_summary_json FROM participant_profile_versions WHERE id = :id"), {"id": version_id}).one()
    assert "Sesame" not in row.snapshot_json
    assert "Confidential note" not in row.snapshot_json
    assert "Sesame" not in row.change_summary_json
