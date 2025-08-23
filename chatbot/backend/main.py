from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from backend import dashboard
from backend.routers import guest

from backend import auth  # ✅ Needed for auth.router
from backend.routers import chat, ingest, files

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(files.router)
app.include_router(dashboard.router)
app.include_router(guest.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
