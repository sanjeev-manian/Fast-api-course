import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..main import app
from ..routers.todos import get_db, get_current_user
from ..models import Base
from ..models import Todo

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionMaker()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"usernmae": "sanjeev", "user_id": 1}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def test_add_todo():
    todo = Todo(task="fast_api", description="learn fast api", priority=5, owner_id=1)
    db = TestingSessionMaker()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


def test_read_all_authenticated(test_add_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "completed": 0,
            "priority": 5,
            "description": "learn fast api",
            "task": "fast_api",
            "owner_id": 1,
            "id": 1,
        }
    ]


def test_read_by_id_authenticated(test_add_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "completed": 0,
        "priority": 5,
        "description": "learn fast api",
        "task": "fast_api",
        "owner_id": 1,
        "id": 1,
    }
