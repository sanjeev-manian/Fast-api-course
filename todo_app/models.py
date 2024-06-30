import sys

sys.path.append(".")

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=1)
    role = Column(String)


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    description = Column(Integer)
    priority = Column(Integer)
    completed = Column(Boolean, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
