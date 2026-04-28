"""Quick tests to verify Docling is installed and working correctly."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_extraction_service import PDFExtractionService


class TestDoclingVerification:
    """Quick verification tests for Docling (fast, mocked)"""
    
    def test_docling_is_installed(self):
        """Verify Docling can be imported"""
        try:
            from docling.document_converter import DocumentConverter
            assert DocumentConverter is not None
        except ImportError as e:
            pytest.fail(f"❌ Docling not installed: {e}")
    
    def test_extract_text_uses_docling(self):
        """Verify extract_text calls Docling DocumentConverter"""
        with patch('app.services.pdf_extraction_service.Path') as mock_path_class, \
             patch('app.services.pdf_extraction_service.DocumentConverter') as mock_converter:
            
            # Mock Path.exists() to return True
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_class.return_value = mock_path_instance
            
            # Setup Docling mock
            mock_instance = MagicMock()
            mock_converter.return_value = mock_instance
            
            mock_doc = MagicMock()
            mock_doc.export_to_markdown.return_value = "# Título\n\nContenido extraído"
            mock_result = MagicMock()
            mock_result.document = mock_doc
            mock_instance.convert.return_value = mock_result
            
            # Call extract_text
            result = PDFExtractionService.extract_text("/tmp/test.pdf")
            
            # Verify Docling was used
            assert mock_converter.called, "DocumentConverter not instantiated"
            assert mock_instance.convert.called, "convert() not called"
            assert mock_doc.export_to_markdown.called, "export_to_markdown() not called"
            assert result == "# Título\n\nContenido extraído"
            print("✅ Docling DocumentConverter being used correctly")
    
    def test_extract_metadata_uses_docling(self):
        """Verify extract_metadata calls Docling"""
        with patch('app.services.pdf_extraction_service.DocumentConverter') as mock_converter:
            # Setup mock
            mock_instance = MagicMock()
            mock_converter.return_value = mock_instance
            
            mock_doc = MagicMock()
            mock_doc.pages = [1, 2, 3]  # 3 pages
            mock_doc.name = "Test Document"
            mock_result = MagicMock()
            mock_result.document = mock_doc
            mock_instance.convert.return_value = mock_result
            
            # Call extract_metadata
            result = PDFExtractionService.extract_metadata("/tmp/test.pdf")
            
            # Verify result structure
            assert result["num_pages"] == 3
            assert result["format"] == "PDF"
            assert result["title"] == "Test Document"
            print("✅ Docling metadata extraction working correctly")
    
    def test_markdown_export_is_used(self):
        """Verify that Docling's markdown export is being used"""
        with patch('app.services.pdf_extraction_service.Path') as mock_path_class, \
             patch('app.services.pdf_extraction_service.DocumentConverter') as mock_converter:
            
            # Mock Path.exists() to return True
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_class.return_value = mock_path_instance
            
            # Setup Docling mock
            mock_instance = MagicMock()
            mock_converter.return_value = mock_instance
            
            mock_doc = MagicMock()
            mock_doc.export_to_markdown.return_value = "## Contenido Markdown\n\nEstructura preservada"
            mock_result = MagicMock()
            mock_result.document = mock_doc
            mock_instance.convert.return_value = mock_result
            
            result = PDFExtractionService.extract_text("/tmp/test.pdf")
            
            # Verify markdown format is returned
            assert "##" in result or "Markdown" in result
            assert mock_doc.export_to_markdown.called
            print("✅ Markdown export format confirmed")
