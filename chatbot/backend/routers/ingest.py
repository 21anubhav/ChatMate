# backend/routers/ingest.py

import os, uuid, shutil
import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.models import Document
from backend.database import get_db
from backend.auth import get_current_user
from backend.pinecone_utils import embed_and_store

UPLOAD_DIR = "uploads"
router = APIRouter()

def pdf_to_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(request)
    session_id = request.cookies.get("session_id")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Convert PDF to .txt temporarily
    txt_path = file_path.replace(".pdf", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(pdf_to_text(file_path))

    # Determine namespace
    if user_id:
        namespace = f"user_{user_id}"
        db_doc = Document(filename=file.filename, file_path=file_path, owner_id=user_id)
        db.add(db_doc)
        db.commit()
    else:
        namespace = f"session_{session_id}"

    # Ingest into Pinecone
    await embed_and_store(txt_path, namespace)

    return RedirectResponse(url="/dashboard", status_code=302)


# Reusable function for guest.py or anywhere
async def process_file(uploaded_file, session_id=None, user_id=None):
    from backend.pinecone_utils import embed_and_store  # to avoid circular import
    from backend.models import Document
    from backend.database import SessionLocal

    db = SessionLocal()
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4()}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file.file, f)

    txt_path = file_path.replace(".pdf", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(pdf_to_text(file_path))

    if user_id:
        namespace = f"user_{user_id}"
        db_doc = Document(filename=uploaded_file.filename, file_path=file_path, owner_id=user_id)
        db.add(db_doc)
        db.commit()
    else:
        namespace = f"session_{session_id}"

    await embed_and_store(txt_path, namespace)
    db.close()
    return namespace
