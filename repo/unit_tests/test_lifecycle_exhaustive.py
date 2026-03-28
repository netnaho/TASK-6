import pytest

from app.core.constants import DeclarationState
from app.core.exceptions import ConflictError
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.declaration_service import DeclarationService


def build_service_context(db_session):
    users = UserRepository(db_session)
    participant = users.get_by_username("participant_demo")
    admin = users.get_by_username("admin_demo")
    profile = ProfileRepository(db_session).get_by_user_id(participant.id)
    plan = PlanRepository(db_session).list_for_participant(participant.id)[0]
    service = DeclarationService(db_session)
    return service, participant, admin, profile, plan


def create_draft_package(db_session):
    service, participant, admin, profile, plan = build_service_context(db_session)
    package = service.create(participant, profile.id, plan.id)
    return service, participant, admin, package


@pytest.mark.parametrize(
    "target_state",
    [
        DeclarationState.DRAFT,
        DeclarationState.SUBMITTED,
        DeclarationState.CORRECTED,
        DeclarationState.WITHDRAWN,
    ],
)
def test_voided_state_rejects_all_other_transitions(db_session, target_state):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(admin, package.id, DeclarationState.VOIDED, reason_text="Administrative closure")
    assert package.state == DeclarationState.VOIDED
    with pytest.raises(ConflictError):
        service.transition(admin, package.id, target_state, reason_text="Illegal transition attempt")


@pytest.mark.parametrize(
    ("starting_state", "target_state", "setup"),
    [
        (DeclarationState.DRAFT, DeclarationState.WITHDRAWN, "draft"),
        (DeclarationState.DRAFT, DeclarationState.CORRECTED, "draft"),
        (DeclarationState.WITHDRAWN, DeclarationState.SUBMITTED, "withdrawn"),
        (DeclarationState.SUBMITTED, DeclarationState.DRAFT, "submitted"),
    ],
)
def test_other_invalid_transitions_raise_conflict(db_session, starting_state, target_state, setup):
    service, participant, admin, package = create_draft_package(db_session)

    if setup == "submitted":
        package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
        assert package.state == starting_state
    elif setup == "withdrawn":
        package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
        package = service.transition(participant, package.id, DeclarationState.WITHDRAWN)
        assert package.state == starting_state
    else:
        assert package.state == starting_state

    with pytest.raises(ConflictError):
        service.transition(participant if target_state != DeclarationState.VOIDED else admin, package.id, target_state, reason_text="Illegal transition attempt")


def test_valid_transition_draft_to_submitted_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    assert package.state == DeclarationState.SUBMITTED


def test_valid_transition_submitted_to_withdrawn_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    package = service.transition(participant, package.id, DeclarationState.WITHDRAWN)
    assert package.state == DeclarationState.WITHDRAWN


def test_valid_transition_submitted_to_voided_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    package = service.transition(admin, package.id, DeclarationState.VOIDED, reason_text="Administrative void")
    assert package.state == DeclarationState.VOIDED


def test_valid_transition_withdrawn_to_draft_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    package = service.transition(participant, package.id, DeclarationState.WITHDRAWN)
    package = service.transition(participant, package.id, DeclarationState.DRAFT)
    assert package.state == DeclarationState.DRAFT


def test_valid_transition_corrected_to_submitted_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    reviewer = UserRepository(db_session).get_by_username("reviewer_demo")
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    correction = service.request_correction(
        reviewer,
        package.id,
        type("Payload", (), {"sections_json": [{"section": "plan"}], "overall_message": "Correct values", "response_due_hours": 24})(),
    )
    service.acknowledge_correction(participant, package.id, correction.id)
    package = service.resubmit_correction(participant, package.id, correction.id, "Updated values")
    assert package.state == DeclarationState.SUBMITTED


def test_valid_transition_draft_to_voided_succeeds(db_session):
    service, participant, admin, package = create_draft_package(db_session)
    package = service.transition(admin, package.id, DeclarationState.VOIDED, reason_text="Administrative void")
    assert package.state == DeclarationState.VOIDED
