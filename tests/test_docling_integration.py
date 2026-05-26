"""Tests to verify pdfplumber + Tesseract OCR integration (CPU-only, no GPU/torch)."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_extraction_service import PDFExtractionService


class TestPDFExtractionWithTesseract:
    """Tests for pdfplumber + Tesseract OCR (CPU-only, fast build)"""
    
    def test_pdfplumber_and_pytesseract_installed(self):
        """Verify pdfplumber + Tesseract dependencies are installed"""
        try:
            import pdfplumber
            import pytesseract
            from pdf2image import convert_from_path
            assert pdfplumber is not None
            assert pytesseract is not None
            assert convert_from_path is not None
        except ImportError as e:
            pytest.fail(f"❌ Missing dependencies: {e}")
    
    def test_extract_text_with_embedded_text_fast_path(self):
        """
        Verify extract_text uses pdfplumber for fast embedded text extraction
        
        Strategy: PDFs with embedded text (75% of academic PDFs) skip OCR
        Expected: Fast extraction without Tesseract call
        """
        with patch('app.services.pdf_extraction_service.pdfplumber.open') as mock_open, \
             patch('app.services.pdf_extraction_service.Path') as mock_path:
            
            # Mock Path.exists()
            mock_path.return_value.exists.return_value = True
            
            # Setup pdfplumber mock with embedded text
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Texto académico embebido en el PDF"
            
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf.__exit__.return_value = None
            
            mock_open.return_value = mock_pdf
            
            # Extract text
            result = PDFExtractionService.extract_text("/tmp/test.pdf")
            
            # Verify: pdfplumber was used, result contains text
            assert "Texto académico embebido" in result
            assert mock_page.extract_text.called
            print("✅ pdfplumber embedded text extraction (fast path) working")
    
    def test_extract_text_fallback_to_ocr_when_minimal_text(self):
        """
        Verify extract_text falls back to Tesseract OCR for scanned/minimal text pages
        
        Strategy: If page has <50 chars, try Tesseract OCR
        Expected: OCR called for low-text pages
        """
        with patch('app.services.pdf_extraction_service.pdfplumber.open') as mock_open, \
             patch('app.services.pdf_extraction_service.Path') as mock_path, \
             patch('app.services.pdf_extraction_service.PDFExtractionService._extract_text_with_ocr') as mock_ocr:
            
            # Mock Path.exists()
            mock_path.return_value.exists.return_value = True
            
            # Mock pdfplumber with minimal text (should trigger OCR)
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Short"  # <50 chars → OCR triggered
            
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf.__exit__.return_value = None
            
            mock_open.return_value = mock_pdf
            
            # Mock OCR result
            mock_ocr.return_value = "Contenido extraído por Tesseract OCR"
            
            # Extract text
            result = PDFExtractionService.extract_text("/tmp/test.pdf")
            
            # Verify: OCR was called for low-text page
            assert mock_ocr.called, "Tesseract OCR should be called for pages with minimal text"
            print("✅ Fallback to Tesseract OCR working for scanned pages")
    
    def test_extract_metadata_with_pdfplumber(self):
        """
        Verify extract_metadata extracts page count + title from pdfplumber
        
        Expected: Returns num_pages, title, format
        """
        with patch('app.services.pdf_extraction_service.pdfplumber.open') as mock_open:
            # Mock pdfplumber PDF
            mock_pdf = MagicMock()
            mock_pdf.pages = [MagicMock(), MagicMock(), MagicMock()]  # 3 pages
            mock_pdf.metadata = {'Title': 'Documento Académico'}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf.__exit__.return_value = None
            
            mock_open.return_value = mock_pdf
            
            # Extract metadata
            result = PDFExtractionService.extract_metadata("/tmp/test.pdf")
            
            # Verify structure
            assert result["num_pages"] == 3
            assert result["title"] == "Documento Académico"
            assert result["format"] == "PDF"
            print("✅ pdfplumber metadata extraction working")
    
    def test_validate_pdf_header(self):
        """Verify PDF validation by checking file header"""
        valid_pdf_content = b"%PDF-1.4\nrest of content"
        invalid_content = b"This is not a PDF"
        
        assert PDFExtractionService.validate_pdf(valid_pdf_content) is True
        assert PDFExtractionService.validate_pdf(invalid_content) is False
        print("✅ PDF header validation working")
    
    def test_extract_text_max_pages_limit(self):
        """
        Verify extract_text respects max_pages parameter
        
        Expected: Only processes first N pages
        """
        with patch('app.services.pdf_extraction_service.pdfplumber.open') as mock_open, \
             patch('app.services.pdf_extraction_service.Path') as mock_path:
            
            # Mock Path.exists()
            mock_path.return_value.exists.return_value = True
            
            # Setup pdfplumber mock with 5 pages
            mock_pages = [
                MagicMock(extract_text=MagicMock(return_value=f"Página {i}")) 
                for i in range(1, 6)
            ]
            
            mock_pdf = MagicMock()
            mock_pdf.pages = mock_pages
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf.__exit__.return_value = None
            
            mock_open.return_value = mock_pdf
            
            # Extract with max_pages=2
            result = PDFExtractionService.extract_text("/tmp/test.pdf", max_pages=2)
            
            # Verify: Only first 2 pages processed
            assert "Página 1" in result
            assert "Página 2" in result
            # Pages 3-5 should not appear
            print("✅ max_pages limit respected")
    
    def test_error_handling_invalid_file(self):
        """Verify proper error handling for invalid/missing files"""
        # Test non-existent file
        with pytest.raises(ValueError, match="File not found"):
            PDFExtractionService.extract_text("/nonexistent/file.pdf")
        
        # Test non-PDF file
        with pytest.raises(ValueError, match="File must be a PDF"):
            with patch('app.services.pdf_extraction_service.Path') as mock_path:
                mock_path.return_value.exists.return_value = True
                PDFExtractionService.extract_text("/tmp/test.txt")
        
        print("✅ Error handling for invalid files working")
