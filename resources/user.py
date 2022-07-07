from http import HTTPStatus
from fastapi import Response

from managers.user import UserManager
from typing import Optional, List

from fastapi import APIRouter, Depends
from managers.auth import oauth2_scheme, is_admin
from models.enums import RoleType
from schemas.response.user import UserOut

router = APIRouter(tags=["Auth"])


@router.get("/users/", dependencies=[Depends(oauth2_scheme), Depends(is_admin)], response_model=List[UserOut], status_code=200)
async def get_all_users(email: Optional[str] = None):
    if email:
        return await UserManager.get_user_by_email(email)
    return await UserManager.get_all_users()


@router.get("/user/", dependencies=[Depends(oauth2_scheme), Depends(is_admin)], status_code=200)
async def get_user_by_email(email: str):
    return await UserManager.get_user_by_email(email)


@router.put("/users/{user_id}/make-admin", dependencies=[Depends(oauth2_scheme), Depends(is_admin)], status_code=204)
async def make_user_admin(user_id: int):
    await UserManager.change_role(RoleType.admin, user_id)
    return Response(status_code=HTTPStatus.NO_CONTENT.value)


@router.put("/users/{user_id}/make-approver", dependencies=[Depends(oauth2_scheme), Depends(is_admin)], status_code=204)
async def make_user_approver(user_id: int):
    await UserManager.change_role(RoleType.approver, user_id)
    return Response(status_code=HTTPStatus.NO_CONTENT.value)
