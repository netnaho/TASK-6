from app.repositories.user_repository import UserRepository
from app.services.declaration_service import DeclarationService


def test_correction_workflow_acknowledge_and_resubmit(db_session):
    users = UserRepository(db_session)
    reviewer = users.get_by_username("reviewer_demo")
    participant = users.get_by_username("participant_demo")
    service = DeclarationService(db_session)
    package = service.list_for_user(participant)[0]
    correction = service.request_correction(
        reviewer,
        package.id,
        type("Payload", (), {"sections_json": [{"section": "plan"}], "overall_message": "Please adjust target values.", "response_due_hours": 24})(),
    )
    acknowledged = service.acknowledge_correction(participant, package.id, correction.id)
    assert acknowledged.status == "acknowledged"
    resubmitted = service.resubmit_correction(participant, package.id, correction.id, "Values updated")
    assert resubmitted.state == "submitted"
