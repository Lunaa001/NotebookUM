"""Routes for document upload and processing."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.models import Document, Usuario
from config import settings

documents_router = APIRouter()


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    model_config = ConfigDict(from_attributes=True)
    
    document_id: int
    status: str
    nombre_archivo: str
    mensaje: str = "Documento almacenado exitosamente"


class DocumentStatusResponse(BaseModel):
    """Response model for document status"""
    model_config = ConfigDict(from_attributes=True)
    
    document_id: int
    nombre_archivo: str
    usuario_id: int
    estado: str = "almacenado"
    fecha_creacion: str


@documents_router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    x_user_id: str = Header("1")
):
    """
    Upload a document and store it.
    
    Args:
        file: PDF or document file
        x_user_id: User ID header
        
    Returns:
        DocumentUploadResponse with document info
    """
    if file is None or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file is required in form field 'file'."
        )

    try:
        usuario_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-ID header value."
        )

    # Validate file exists
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty."
        )
    
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed: {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    await file.seek(0)

    # Create temporary file for storage
    suffix = Path(file.filename).suffix or ".pdf"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="uploads") as tmp_file:
            tmp_file.write(content)
            temp_path = tmp_file.name
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to store file: {str(e)}"
        )

    # Simulated response (BD integration in Fase 3)
    return DocumentUploadResponse(
        document_id=1,
        status="almacenado",
        nombre_archivo=file.filename,
        mensaje=f"Documento '{file.filename}' cargado exitosamente"
    )


@documents_router.get("/{document_id}", response_model=DocumentStatusResponse)
async def get_document(document_id: int):
    """
    Get document information by ID.
    
    Args:
        document_id: Document ID
        
    Returns:
        DocumentStatusResponse with document details
    """
    if document_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )

    # This would query the database - for now return template
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document with ID {document_id} not found"
    )


@documents_router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: int):
    """
    Get document processing status.
    
    Args:
        document_id: Document ID
        
    Returns:
        DocumentStatusResponse with document status
    """
    if document_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document with ID {document_id} not found"
    )