"""
Service for extracting text from PDF files via extract-service microservice.
This service communicates with the extract-service microservice to extract text from PDFs.
"""

from typing import Optional
from pathlib import Path
import logging
import base64

import requests
from requests.exceptions import RequestException

from config import settings

logger = logging.getLogger(__name__)


class PDFExtractionService:
    """
    Service for extracting text from PDF files via extract-service microservice.
    
    Uses the extract-service microservice for:
    - pdfplumber: For embedded text extraction (fast, no OCR needed)
    - Tesseract: For OCR when text is not embedded (scanned PDFs, images)
    """
    
    # Extract service configuration
    EXTRACT_PROCESS_ENDPOINT = f"{settings.EXTRACT_SERVICE_URL}/api/v1/pdf/process"
    EXTRACT_METADATA_ENDPOINT = f"{settings.EXTRACT_SERVICE_URL}/api/v1/pdf/metadata"
    
    @staticmethod
    def extract_text(file_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extract text from PDF file via extract-service microservice.
        
        Args:
            file_path: Path to the PDF file
            max_pages: Maximum number of pages to extract (None for all)
        
        Returns:
            Extracted text content with preserved structure
        
        Raises:
            ValueError: If file is not a valid PDF or cannot be processed
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            # Validate PDF signature
            if not PDFExtractionService.validate_pdf(pdf_content):
                raise ValueError("File must be a valid PDF")
            
            # Encode PDF to base64
            file_name = path.name
            content_b64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Prepare request payload
            payload = {
                "file_name": file_name,
                "content": content_b64,
            }
            
            if max_pages is not None:
                payload["max_pages"] = max_pages
            
            # Call extract-service
            logger.info(f"Sending PDF to extract-service: {file_name}")
            response = requests.post(
                PDFExtractionService.EXTRACT_PROCESS_ENDPOINT,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            extracted_text = result.get("content", "")
            
            logger.info(f"Successfully extracted text from {file_name}")
            return extracted_text
        
        except requests.exceptions.ConnectionError as e:
            raise ValueError(f"Cannot connect to extract-service: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise ValueError(f"extract-service timeout: {str(e)}")
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_detail = e.response.json().get("detail", str(e))
                error_msg = f"Extract service error: {error_detail}"
            except:
                pass
            raise ValueError(error_msg)
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Extract PDF metadata via extract-service microservice.
        
        Args:
            file_path: Path to the PDF file
        
        Returns:
            Dict with num_pages, title, and format
            
        Raises:
            ValueError: If file does not exist or cannot be processed
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            # Validate PDF signature
            if not PDFExtractionService.validate_pdf(pdf_content):
                raise ValueError("File must be a valid PDF")
            
            # Encode PDF to base64
            file_name = path.name
            content_b64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Prepare request payload
            payload = {
                "file_name": file_name,
                "content": content_b64,
            }
            
            # Call extract-service
            logger.info(f"Requesting metadata from extract-service: {file_name}")
            response = requests.post(
                PDFExtractionService.EXTRACT_METADATA_ENDPOINT,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            metadata = result.get("metadata", {})
            
            logger.info(f"Successfully extracted metadata from {file_name}")
            return metadata
        
        except requests.exceptions.ConnectionError as e:
            raise ValueError(f"Cannot connect to extract-service: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise ValueError(f"extract-service timeout: {str(e)}")
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_detail = e.response.json().get("detail", str(e))
                error_msg = f"Extract service error: {error_detail}"
            except:
                pass
            raise ValueError(error_msg)
        except Exception as e:
            raise ValueError(f"Error extracting PDF metadata: {str(e)}")
    
    @staticmethod
    def validate_pdf(file_content: bytes) -> bool:
        """
        Validate if content is a valid PDF by checking file header.
        
        Args:
            file_content: Raw file bytes
        
        Returns:
            True if valid PDF, False otherwise
        """
        return file_content.startswith(b"%PDF")
