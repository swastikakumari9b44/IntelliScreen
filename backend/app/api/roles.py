from fastapi import APIRouter

from app.roles import list_roles
from app.schemas.schemas import RoleOut

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=list[RoleOut])
def get_roles():
    return [
        RoleOut(id=r.id, label=r.label, description=r.description)
        for r in list_roles()
    ]
