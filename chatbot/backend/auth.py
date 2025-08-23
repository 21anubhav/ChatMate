from fastapi import APIRouter, Request, Form, Response, status, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User
from itsdangerous import URLSafeSerializer, BadSignature
from dotenv import load_dotenv
import hashlib
import os
import uuid

# Load .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "your_fallback_key")

# Secure serializer
serializer = URLSafeSerializer(SECRET_KEY)

# Jinja templates
templates = Jinja2Templates(directory="frontend/templates")

# FastAPI router
router = APIRouter()

# ---------------------- UTILS ---------------------- #


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_session_cookie(user_id: int):
    return serializer.dumps({"user_id": user_id})


def get_current_user(request: Request) -> int | None:
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            data = serializer.loads(session_cookie)
            return data.get("user_id")
        except BadSignature:
            return None
    return None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- ROUTES ---------------------- #


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "auth.html", {"request": request, "mode": "login"}
    )


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "mode": "login", "error": "Invalid email or password"},
            status_code=401,
        )

    session_token = create_session_cookie(user.id)
    redirect = RedirectResponse(url="/dashboard", status_code=302)
    redirect.set_cookie(key="session", value=session_token, httponly=True)
    redirect.delete_cookie("session_id")  # remove guest session if logging in
    return redirect


@router.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "auth.html", {"request": request, "mode": "signup"}
    )


@router.post("/signup")
async def signup(
    request: Request,
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)

    existing_user = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )

    if existing_user:
        return templates.TemplateResponse(
            "auth.html",
            {
                "request": request,
                "mode": "signup",
                "signup_error": "Username or email already exists",
            },
            status_code=400,
        )

    new_user = User(username=username, email=email, password=hash_password(password))
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login", status_code=302)


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    response.delete_cookie("session_id")  # clean guest cookie
    return response


# ---------------------- GUARD ---------------------- #


def require_login(request: Request) -> int:
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse(url="/", status_code=302)
    return user_id