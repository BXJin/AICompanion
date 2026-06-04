from fastapi import APIRouter

from app.dependencies import AdminUserDep
from app.schemas.admin import AdminUserSummaryResponse

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("/me", response_model=AdminUserSummaryResponse)
async def get_admin_me(admin: AdminUserDep) -> AdminUserSummaryResponse:
    return AdminUserSummaryResponse(admin_id=admin.admin_id, roles=admin.roles)

