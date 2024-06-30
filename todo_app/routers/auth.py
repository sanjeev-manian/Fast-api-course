from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "9047344945abcdef"  # hexadecimal string
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# crypt context - Helper for hashing & verifying passwords using multiple algorithms.
# bcrypt - hashing algorithm
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/authenticate_user")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate(db: db_dependency, email: str, password: str):
    user_model = db.query(User).filter(User.email == email).first()
    if user_model is None:
        return False
    if bcrypt_context.verify(password, user_model.hashed_password):
        return user_model
    return False


# encode
def create_access_token(user_name: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": user_name, "id": user_id}
    expires = datetime.now() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# decode
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            return None
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


class UserRequest(BaseModel):
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=5, max_length=20)
    first_name: str = Field(min_length=5, max_length=20)
    last_name: Optional[str] = None
    role: str = None


# ------------------------------------------

templates = Jinja2Templates(directory="templates")


class LoginForm:
    def __init__(self, request: Request):
        self.request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def get_username_password_from_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.get_username_password_from_form()
        response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except:
        msg = "Unknown Error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Logout Successful"
    respose = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    respose.delete_cookie(key="access_token")
    return respose


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    db: db_dependency,
    email: str = Form(),
    role: str = Form(),
    firstname: str = Form(),
    lastname: str = Form(),
    password: str = Form(),
    password2: str = Form(),
):
    if password != password2:
        msg = "Password mismatch"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    user_model_check = db.query(User).filter(User.email == email).first()
    if user_model_check is not None:
        msg = "Email already exist"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    user_model = User(
        email=email,
        first_name=firstname,
        last_name=lastname,
        hashed_password=bcrypt_context.hash(password),
        is_active=True,
        role=role,
    )
    db.add(user_model)
    db.commit()
    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


# -----------------------------------------------


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, new_user: UserRequest):

    user_model = User(
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        hashed_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role,
    )

    db.add(user_model)
    db.commit()


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    response: Response,
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    authenticated_user = authenticate(db, form_data.username, form_data.password)
    if authenticated_user is False:
        return False
    else:
        token = create_access_token(
            user_name=authenticated_user.email,
            user_id=authenticated_user.id,
            expires_delta=timedelta(minutes=20),
        )
        response.set_cookie(key="access_token", value=token, httponly=True)
        # return {"access_token": token, "token_type": "bearer"}
        return True
