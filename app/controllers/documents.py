"""Routes for document upload and processing."""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Header, HTTPException, status, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_session
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.services.pdf_extraction_service import PDFExtractionService
from app.services.ai_service import AIService
from app.services.summary_service import SummaryService
from config import settings

documents_router = APIRouter()


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    model_config = ConfigDict(from_attributes=True)
    
    document_id: int
    nombre_archivo: str
    status: str = "almacenado"
    mensaje: str = "Documento almacenado y procesado exitosamente"


class DocumentResponse(BaseModel):
    """Response model for document details"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    usuario_id: int
    nombre_archivo: str
    texto_extraido: str | None = None
    fecha_creacion: str


class SummaryGenerationRequest(BaseModel):
    """Request model for generating a summary"""
    max_tokens: int = 300


class SummaryResponse(BaseModel):
    """Response model for summary generation"""
    document_id: int
    status: str
    resumen: str
    resumen_longitud: int
    mensaje: str = "Resumen generado exitosamente"


@documents_router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    x_user_id: str = Header("1"),
    session: Session = Depends(get_session)
):
    """
    Upload a PDF document, extract text, and store it.
    
    Args:
        file: PDF file to upload
        x_user_id: User ID from header
        session: Database session
        
    Returns:
        DocumentUploadResponse with document info
    """
    try:
        if file is None or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A PDF file is required in form field 'file'."
            )

        try:
            usuario_id = int(x_user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-User-ID header value."
            )

        # Read file content
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

        # Validate PDF
        if not PDFExtractionService.validate_pdf(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a valid PDF."
            )

        # Save file
        storage = StorageService()
        file_path = storage.save_file(content, file.filename)

        # Extract text from PDF
        try:
            texto_extraido = PDFExtractionService.extract_text(file_path, max_pages=10)
        except ValueError as e:
            storage.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing PDF: {str(e)}"
            )

        # Create document in database
        doc_service = DocumentService(session)
        documento = doc_service.create({
            "usuario_id": usuario_id,
            "nombre_archivo": file.filename,
            "ruta_archivo": file_path,
            "texto_extraido": texto_extraido,
        })

        return DocumentUploadResponse(
            document_id=documento.id,
            nombre_archivo=documento.nombre_archivo,
            status="almacenado",
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing document"
        )
    finally:
        session.close()


@documents_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    session: Session = Depends(get_session)
):
    """
    Get document information by ID.
    
    Args:
        document_id: Document ID
        session: Database session
        
    Returns:
        DocumentResponse with document details
    """
    try:
        if document_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID"
            )

        doc_service = DocumentService(session)
        documento = doc_service.get_by_id(document_id)

        return DocumentResponse(
            id=documento.id,
            usuario_id=documento.usuario_id,
            nombre_archivo=documento.nombre_archivo,
            texto_extraido=documento.texto_extraido,
            fecha_creacion=documento.fecha_creacion.isoformat() if documento.fecha_creacion else None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document"
        )
    finally:
        session.close()


@documents_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        session: Database session
    """
    try:
        if document_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID"
            )

        doc_service = DocumentService(session)
        documento = doc_service.get_by_id(document_id)
        
        # Delete file from storage
        storage = StorageService()
        if documento.ruta_archivo:
            storage.delete_file(documento.ruta_archivo)

        # Delete from database
        doc_service.delete(document_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )
    finally:
        session.close()


@documents_router.post("/{document_id}/summary", response_model=SummaryResponse, status_code=status.HTTP_200_OK)
async def generate_document_summary(
    document_id: int,
    request: SummaryGenerationRequest,
    session: Session = Depends(get_session)
):
    """
    Generate and store AI summary for a document.
    
    Args:
        document_id: Document ID
        request: Summary generation request with max_tokens
        session: Database session
        
    Returns:
        SummaryResponse with generated summary
    """
    try:
        if document_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID"
            )

        # Get document
        doc_service = DocumentService(session)
        documento = doc_service.get_by_id(document_id)

        # Check if document has extracted text
        if not documento.texto_extraido or not documento.texto_extraido.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no extracted text for summarization"
            )

        # Generate summary using AIService and SummaryService
        ai_service = AIService(api_key=os.getenv("OPENAI_API_KEY"))
        summary_service = SummaryService(ai_service=ai_service)

        # Check if summarization is feasible
        if not summary_service.should_generate_summary(documento.texto_extraido):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document text too short for meaningful summarization (minimum 100 characters)"
            )

        # Generate summary
        try:
            resumen = summary_service.generate_summary(
                document_text=documento.texto_extraido,
                max_tokens=request.max_tokens
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error generating summary: {str(e)}"
            )

        # Store summary in database
        documento.resumen = resumen
        session.commit()

        return SummaryResponse(
            document_id=documento.id,
            status="generado",
            resumen=resumen,
            resumen_longitud=len(resumen),
            mensaje="Resumen generado exitosamente"
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating summary"
        )
    finally:
        session.close()
