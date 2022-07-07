from fastapi import APIRouter
from managers.user import UserManager
from schemas.request.user import UserRegisterIn, UserLoginIn

from fastapi import APIRouter, Depends
from managers.auth import oauth2_scheme, is_complainer, is_admin, is_approver
from fastapi.encoders import jsonable_encoder

router = APIRouter(tags=["Auth"])


@router.post("/register/", status_code=201)
async def register(user_data: UserRegisterIn):
    token = await UserManager.register(user_data.dict())
    return {"token": token}


@router.post("/login/")
async def login(user_data: UserLoginIn):
    token = await UserManager.login(user_data.dict())
    return {"token": token}
