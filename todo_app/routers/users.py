from fastapi import APIRouter, Form, Request
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from starlette import status
from passlib.context import CryptContext

from .auth import get_current_user

from ..models import User
from ..database import SessionLocal

router = APIRouter(prefix="/user", tags=["users"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(min_length=5, max_length=20)
    new_password: str = Field(min_length=5, max_length=20)


# -----------------------------------------

templates = Jinja2Templates(directory="templates")


@router.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, db: db_dependency):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": user_model}
    )


@router.get("/change_password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "change-password.html", {"request": request, "user": user}
    )


@router.post("/change_password", response_class=HTMLResponse)
async def change_password_page(
    request: Request,
    db: db_dependency,
    old_password: str = Form(),
    new_password: str = Form(),
    confirm_password: str = Form(),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    if not bcrypt_context.verify(old_password, user_model.hashed_password):
        msg = "Incorrect old password"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "msg": msg, "user": user}
        )
    if new_password != confirm_password:
        msg = "Password mismatch new and confirm"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "msg": msg}
        )
    user_model.hashed_password = bcrypt_context.hash(new_password)
    db.add(user_model)
    db.commit()
    msg = "Password changed"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


# --------------------------------------------------------


@router.put("/update_password", status_code=status.HTTP_201_CREATED)
async def update_password(
    db: db_dependency,
    user: user_dependency,
    update_password_body: UpdatePasswordRequest,
):

    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    if not bcrypt_context.verify(
        update_password_body.old_password, user_model.hashed_password
    ):
        return "Invalid old password"
    user_model.hashed_password = bcrypt_context.hash(update_password_body.new_password)
    db.add(user_model)
    db.commit()
