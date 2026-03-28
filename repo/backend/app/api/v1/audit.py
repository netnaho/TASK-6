from fastapi import APIRouter, Depends

from app.api.deps import DBSession, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.services.admin_service import AdminService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter()


@router.get("")
def list_audit_logs(db: DBSession, params: PaginationParams = Depends(), user=Depends(require_roles(Role.ADMINISTRATOR))):
    service = AdminService(db)
    paginated = paginate_query(db, service.audit_logs_stmt(), params)
    return success_response(paginated.items, meta=paginated.meta)
