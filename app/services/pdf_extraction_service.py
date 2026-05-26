"""Service for extracting text from PDF files using pdfplumber + Tesseract OCR (CPU-only)."""

from typing import Optional
from pathlib import Path
import logging

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

logger = logging.getLogger(__name__)


class PDFExtractionService:
    """
    Service for extracting text from PDF files using:
    - pdfplumber: For embedded text extraction (fast, no OCR needed)
    - Tesseract: For OCR when text is not embedded (scanned PDFs, images)
    
    CPU-only implementation without GPU/torch dependencies.
    """
    
    @staticmethod
    def extract_text(file_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extract text from PDF file with fallback to OCR for scanned pages.
        
        Strategy:
        1. Try pdfplumber first (for PDFs with embedded text) - FAST (~0.1-0.5s)
        2. If minimal text found, use Tesseract OCR on page images - SLOWER (~1-3s per page)
        
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
            all_text = []
            
            # Step 1: Try pdfplumber for embedded text (fast path)
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
                
                logger.info(f"Processing PDF: {total_pages} pages (limit: {pages_to_process})")
                
                for page_idx, page in enumerate(pdf.pages[:pages_to_process]):
                    try:
                        # Extract embedded text
                        text = page.extract_text()
                        
                        # If page has minimal text, try OCR
                        if not text or len(text.strip()) < 50:
                            logger.debug(f"Page {page_idx + 1}: Limited embedded text, attempting OCR")
                            ocr_text = PDFExtractionService._extract_text_with_ocr(file_path, page_idx)
                            text = text if text else ocr_text
                        
                        if text:
                            all_text.append(f"--- Page {page_idx + 1} ---\n{text}\n")
                        
                    except Exception as e:
                        logger.warning(f"Error processing page {page_idx + 1}: {str(e)}")
                        continue
            
            result = "\n".join(all_text).strip()
            return result if result else ""
        
        except pdfplumber.PDFException as e:
            raise ValueError(f"Invalid PDF file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def _extract_text_with_ocr(file_path: str, page_num: int) -> str:
        """
        Extract text from a specific PDF page using Tesseract OCR.
        
        Args:
            file_path: Path to PDF
            page_num: Zero-indexed page number
        
        Returns:
            Extracted text from OCR
        """
        try:
            # Convert PDF page to image (300 DPI for better OCR accuracy)
            images = convert_from_path(
                file_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )
            
            if not images:
                return ""
            
            # Run Tesseract OCR on the image
            image = images[0]
            text = pytesseract.image_to_string(image, lang='spa+eng')
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"OCR failed for page {page_num + 1}: {str(e)}")
            return ""
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Extract PDF metadata including page count.
        
        Args:
            file_path: Path to the PDF file
        
        Returns:
            Dict with num_pages, title (filename), and format
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                title = pdf.metadata.get('Title', 'Unknown') if pdf.metadata else 'Unknown'
            
            return {
                "num_pages": page_count,
                "title": title,
                "format": "PDF"
            }
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {str(e)}")
            return {
                "num_pages": 0,
                "title": "Unknown",
                "format": "PDF",
                "error": str(e)
            }
    
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
