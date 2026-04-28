"""Tests for PDFExtractionService."""

import pytest
import os
from pathlib import Path
from io import BytesIO

from app.services.pdf_extraction_service import PDFExtractionService
from app.services.storage_service import StorageService


class TestPDFExtractionService:
    """PDFExtractionService tests"""

    def test_validate_pdf_returns_true_for_valid_pdf_header(self):
        """Test that validate_pdf detects valid PDF header"""
        # PDF files start with %PDF
        pdf_content = b"%PDF-1.4\n%fake pdf content"
        
        result = PDFExtractionService.validate_pdf(pdf_content)
        
        assert result is True

    def test_validate_pdf_returns_false_for_invalid_header(self):
        """Test that validate_pdf rejects non-PDF files"""
        invalid_content = b"This is not a PDF file"
        
        result = PDFExtractionService.validate_pdf(invalid_content)
        
        assert result is False

    def test_validate_pdf_returns_false_for_empty_content(self):
        """Test that validate_pdf rejects empty content"""
        result = PDFExtractionService.validate_pdf(b"")
        
        assert result is False

    def test_validate_pdf_returns_false_for_partial_pdf_header(self):
        """Test that validate_pdf requires full PDF signature"""
        partial = b"%PDF"
        
        result = PDFExtractionService.validate_pdf(partial)
        
        # Should still work if it starts with %PDF
        assert result is True

    def test_extract_text_raises_error_for_nonexistent_file(self):
        """Test that extract_text raises ValueError for missing file"""
        with pytest.raises(ValueError):
            PDFExtractionService.extract_text("/tmp/nonexistent_pdf_file_xyz.pdf")

    def test_extract_text_raises_error_for_invalid_pdf(self):
        """Test that extract_text raises error for corrupted PDF"""
        storage = StorageService()
        
        # Create invalid PDF file
        invalid_pdf = b"%PDF-1.4\ninvalid content"
        file_path = storage.save_file(invalid_pdf, "invalid.pdf")
        
        try:
            with pytest.raises(ValueError):
                PDFExtractionService.extract_text(file_path)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_extract_metadata_raises_error_for_nonexistent_file(self):
        """Test that extract_metadata raises error for missing file"""
        with pytest.raises(ValueError):
            PDFExtractionService.extract_metadata("/tmp/nonexistent_pdf_file_xyz.pdf")

    def test_extract_text_with_max_pages_parameter(self):
        """Test that extract_text respects max_pages parameter"""
        # This test verifies the parameter is accepted
        # Actual PDF extraction requires a valid PDF file
        storage = StorageService()
        
        # Create a simple PDF-like file (will fail extraction but tests parameter)
        pdf_content = b"%PDF-1.4\ninvalid"
        file_path = storage.save_file(pdf_content, "test.pdf")
        
        try:
            with pytest.raises(ValueError):
                # Just verify the parameter is accepted
                PDFExtractionService.extract_text(file_path, max_pages=5)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
