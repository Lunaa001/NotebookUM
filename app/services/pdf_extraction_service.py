from docling.document_converter import DocumentConverter
from typing import Optional
from pathlib import Path


class PDFExtractionService:
    """Service for extracting text from PDF files using Docling"""
    
    @staticmethod
    def extract_text(file_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extract text from PDF file with support for complex layouts, tables, and OCR
        
        Args:
            file_path: Path to the PDF file
            max_pages: Maximum number of pages to extract (None for all)
        
        Returns:
            Extracted text content with preserved formatting
        
        Raises:
            ValueError: If file is not a valid PDF
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)
            document = result.document
            
            # Export to markdown for better readability and structure preservation
            full_text = document.export_to_markdown()
            
            # Handle max_pages limitation
            if max_pages:
                lines = full_text.split('\n')
                # Estimate page breaks (~40-50 lines per page)
                max_lines = max_pages * 50
                full_text = '\n'.join(lines[:max_lines])
            
            return full_text if full_text else ""
        
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extract PDF metadata including page count"""
        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)
            document = result.document
            
            # Count pages by checking page refs in the document
            page_count = len(document.pages) if hasattr(document, 'pages') else 1
            
            return {
                "num_pages": page_count,
                "title": document.name if hasattr(document, 'name') else "Unknown",
                "format": "PDF"
            }
        except Exception as e:
            raise ValueError(f"Error extracting PDF metadata: {str(e)}")
    
    @staticmethod
    def validate_pdf(file_content: bytes) -> bool:
        """Validate if content is a valid PDF by checking header"""
        return file_content.startswith(b"%PDF")
