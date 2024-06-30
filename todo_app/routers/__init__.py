"""Init File."""

from fastapi import APIRouter

from . import auth
from . import todos
from . import users
from . import admin

router = APIRouter()

router.include_router(auth.router)
router.include_router(todos.router)
router.include_router(users.router)
router.include_router(admin.router)
