"""Routes for document upload and asynchronous processing."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from celery.exceptions import CeleryError
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models.document import HistorialDocumento
from app.services.async_tasks import process_document_task
from app.services.validation import (
    create_rfc9457_error,
    validate_file_size,
    validate_pdf_content_type,
)
from app.utils.errors import internal_server_error, not_found
from config import settings

documents_router = APIRouter()


class DocumentStatusResponse(BaseModel):
    document_id: int
    status: str
    created_at: str | None = None


class DocumentUploadResponse(BaseModel):
    document_id: int
    status: str
    job_id: str
    status_url: str


@documents_router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    x_user_id: str = Header("1")
):
    """Upload a PDF document and enqueue asynchronous processing."""
    if file is None or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A PDF file is required in form field 'file'."
        )

    try:
        # Read file content to validate
        content = await file.read()
        await file.seek(0)
        
        # Create a mock object with required attributes for validation
        class FileWrapper:
            def __init__(self, upload_file, content):
                self.upload_file = upload_file
                self.content = content
                self.filename = upload_file.filename
                self.content_type = upload_file.content_type
                self.content_length = len(content)
            
            def stream_seek(self):
                pass
        
        file_wrapper = FileWrapper(file, content)
        validate_pdf_content_type(file_wrapper)
        validate_file_size(file_wrapper, max_size=settings.MAX_UPLOAD_SIZE)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    try:
        usuario_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-ID header value."
        )

    suffix = Path(file.filename).suffix or ".pdf"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(content)
            temp_pdf_path = tmp_file.name
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store uploaded file for processing."
        )

    document = HistorialDocumento(
        usuario_id=usuario_id,
        nombre_archivo=file.filename,
        tamanio_bytes=len(content),
        estado="pending",
    )
    try:
        db.session.add(document)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        _safe_delete(temp_pdf_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to persist document metadata."
        )

    try:
        task_result = process_document_task.delay(
            user_id=usuario_id,
            document_id=document.id,
            pdf_path=temp_pdf_path,
        )
    except (CeleryError, RuntimeError):
        document.estado = "failed"
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        _safe_delete(temp_pdf_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to enqueue document processing task."
        )

    return DocumentUploadResponse(
        document_id=document.id,
        status="pending",
        job_id=task_result.id,
        status_url=f"/api/v1/documento/{document.id}/status",
    )


@documents_router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: int):
    """Return current processing status for an uploaded document."""
    document = db.session.get(HistorialDocumento, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    return DocumentStatusResponse(
        document_id=document.id,
        status=document.estado,
        created_at=document.created_at.isoformat() if document.created_at else None,
    )


def _safe_delete(path: str) -> None:
    """Delete a temporary file if it exists."""
    if os.path.exists(path):
        os.remove(path)