# backend/routers/dashboard.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = require_login(request)
    if isinstance(user_id, RedirectResponse):
        return user_id  # redirect if not logged in
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user_id": user_id}
    )
