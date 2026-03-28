import pytest

from app.core.constants import DeclarationState
from app.core.exceptions import ConflictError
from app.repositories.plan_repository import PlanRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.declaration_service import DeclarationService


def test_legal_and_illegal_declaration_transitions(db_session):
    users = UserRepository(db_session)
    participant = users.get_by_username("participant_demo")
    profile = ProfileRepository(db_session).get_by_user_id(participant.id)
    plan = PlanRepository(db_session).list_for_participant(participant.id)[0]
    service = DeclarationService(db_session)
    package = service.create(participant, profile.id, plan.id)
    package = service.transition(participant, package.id, DeclarationState.SUBMITTED)
    assert package.state == DeclarationState.SUBMITTED
    with pytest.raises(ConflictError):
        service.transition(participant, package.id, DeclarationState.DRAFT)
