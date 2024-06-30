from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import get_current_user

from ..models import Todo, User
from ..database import SessionLocal

router = APIRouter(tags=["admin"], prefix="/admin")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/all_users")
async def view_all_users(db: db_dependency, user: user_dependency):

    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    if not user_model.role == "admin":
        return {"message": "Not Authorized to access this url"}

    return db.query(User).all()


@router.get("/all_todos")
async def view_all_todos(db: db_dependency, user: user_dependency):

    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    if not user_model.role == "admin":
        return {"message": "Not Authorized to access this url"}

    todo_model = db.query(Todo).all()
    return todo_model


@router.get("/all_todos/{user_id}")
async def view_todos_user_id(db: db_dependency, user: user_dependency, user_id: int):

    user_model = db.query(User).filter(User.id == user["user_id"]).first()
    if not user_model.role == "admin":
        return {"message": "Not Authorized to access this url"}

    todo_model = db.query(Todo).filter(Todo.owner_id == user_id).all()
    return todo_model
