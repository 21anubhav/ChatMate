from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from uuid import uuid4
from fastapi.templating import Jinja2Templates
from backend.routers.ingest import process_file
from backend.pinecone_utils import index
from backend.azure_openai_utils import stream_chat_with_documents
import os

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@router.post("/upload-guest")
async def upload_guest(request: Request, file: UploadFile = File(...)):
    session_id = request.cookies.get("guest_session")
    if not session_id:
        session_id = str(uuid4())

    # 🧹 Clean up any previous guest session data
    await delete_guest_data(session_id)

    # 📥 Ingest new document (stored in Pinecone with guest namespace)
    await process_file(file, session_id=session_id)

    # 🍪 Set session cookie and redirect to chat
    response = RedirectResponse(url="/guest-chat", status_code=302)
    response.set_cookie("guest_session", session_id, httponly=True)
    return response


@router.get("/guest-chat", response_class=HTMLResponse)
async def guest_chat_page(request: Request):
    session_id = request.cookies.get("guest_session")
    if not session_id:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("guest_chat.html", {"request": request})


@router.post("/guest-chat/stream")
async def guest_chat_stream(request: Request):
    form = await request.form()
    query = form.get("query", "").strip()
    session_id = request.cookies.get("guest_session")
    if not session_id:
        return StreamingResponse(iter(["Session not found."]), media_type="text/plain")

    namespace = f"session_{session_id}"

    async def event_generator():
        async for chunk in stream_chat_with_documents(query, namespace=namespace):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/plain")


@router.get("/guest-logout")
async def guest_logout(request: Request):
    session_id = request.cookies.get("guest_session")
    if session_id:
        await delete_guest_data(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("guest_session")
    return response


# Utility: Delete namespace from Pinecone
async def delete_guest_data(session_id: str):
    namespace = f"session_{session_id}"
    try:
        index.delete(delete_all=True, namespace=namespace)
    except Exception as e:
        print(f"⚠️ Error deleting guest data for {namespace}: {e}")
