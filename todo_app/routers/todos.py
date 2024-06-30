from fastapi import APIRouter, Form, Request
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from .auth import get_current_user

from ..models import Todo
from ..database import engine, SessionLocal

router = APIRouter(tags=["todos"])

templates = Jinja2Templates(directory="templates")


# Dependency function helps to open database, and return session for request
# Closes the database while response
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    task: str = Field(min_length=3)
    description: Optional[str] = None
    priority: int = Field(gt=0, lt=6)
    completed: bool = Field(default=0)


# --------------------------------


@router.get("/home", response_class=HTMLResponse)
async def home_page(db: db_dependency, request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todo).filter(Todo.owner_id == user["user_id"]).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user}
    )


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    db: db_dependency,
    task: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    todo_model = Todo()
    todo_model.task = task
    todo_model.description = description
    todo_model.priority = priority
    todo_model.owner_id = user["user_id"]
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.get("/edit/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: db_dependency):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo_model, "user": user}
    )


@router.post("/edit/{todo_id}", response_class=HTMLResponse)
async def edit_new_todo(
    request: Request,
    db: db_dependency,
    todo_id: int,
    task: str = Form(),
    description: str = Form(),
    priority: str = Form(),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    todo_model.task = task
    todo_model.description = description
    todo_model.priority = priority
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_the_todo(request: Request, db: db_dependency, todo_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user["user_id"])
    )
    if todo_model is None:
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def completed_the_task(request: Request, db: db_dependency, todo_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="auth/login", status_code=status.HTTP_302_FOUND)
    db.query(Todo).filter(Todo.id == todo_id).first().completed = (
        not db.query(Todo).filter(Todo.id == todo_id).first().completed
    )
    db.commit()
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


# -----------------------------------


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(
    db: db_dependency,
    user: user_dependency,
):
    # Depends->dependency injection
    return db.query(Todo).filter(Todo.owner_id == user["user_id"]).all()
    # database is passed when the endpoint is hit


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(
    db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)
):
    todo_model = (
        db.query(Todo)
        .filter(Todo.owner_id == user["user_id"])
        .filter(Todo.id == todo_id)
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    db: db_dependency,
    user: user_dependency,
    new_todo: TodoRequest,
):
    new_todo_object = Todo(**new_todo.model_dump())
    new_todo_object.owner_id = user["user_id"]
    db.add(new_todo_object)
    db.commit()


@router.put("/todo/update_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency,
    user: user_dependency,
    update_todo: TodoRequest,
    todo_id: int = Path(gt=0),
):

    todo_model = (
        db.query(Todo)
        .filter(Todo.owner_id == user["user_id"])
        .filter(Todo.id == todo_id)
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo not found")

    todo_model.task = update_todo.task
    todo_model.description = update_todo.description
    todo_model.priority = update_todo.priority
    todo_model.completed = update_todo.completed

    db.add(todo_model)
    db.commit()


@router.delete("/todo/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)
):

    todo_model = (
        db.query(Todo)
        .filter(Todo.owner_id == user["user_id"])
        .filter(Todo.id == todo_id)
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.delete()
    # or
    # db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
