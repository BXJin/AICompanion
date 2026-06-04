from pydantic import BaseModel


class AdminUserSummaryResponse(BaseModel):
    admin_id: str
    roles: list[str]
    boundary: str = "admin"

