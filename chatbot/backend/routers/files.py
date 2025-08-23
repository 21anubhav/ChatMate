from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Document
from backend.auth import get_current_user
from backend.pinecone_utils import delete_namespace_file

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/files")
def list_files(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user(request)
    if not user_id:
        return {"files": []}
    docs = db.query(Document).filter_by(owner_id=user_id).all()
    return {"files": [{"id": d.id, "name": d.filename} for d in docs]}

@router.get("/delete-file/{doc_id}")
def delete_file(doc_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user(request)
    doc = db.query(Document).filter_by(id=doc_id, owner_id=user_id).first()
    if doc:
        delete_namespace_file(doc.file_path, f"user_{user_id}")
        db.delete(doc)
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=302)
