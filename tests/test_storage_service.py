"""Tests for StorageService."""

import pytest
import os
from pathlib import Path

from app.services.storage_service import StorageService


class TestStorageService:
    """StorageService tests"""

    def test_save_file_creates_unique_filename(self):
        """Test that save_file creates unique filenames"""
        service = StorageService()
        
        content = b"test file content"
        filename = "test.pdf"
        
        file_path = service.save_file(content, filename)
        
        assert file_path is not None
        assert os.path.exists(file_path)
        assert Path(file_path).name.endswith(".pdf")
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_save_file_creates_directory_if_not_exists(self):
        """Test that save_file creates upload directory"""
        service = StorageService()
        upload_dir = Path("/tmp/notebookum_uploads")
        
        content = b"test content"
        filename = "test.txt"
        
        file_path = service.save_file(content, filename)
        
        assert upload_dir.exists()
        assert os.path.exists(file_path)
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_file_exists_returns_true_for_existing_file(self):
        """Test that file_exists detects existing files"""
        service = StorageService()
        
        content = b"test content"
        filename = "test.txt"
        
        file_path = service.save_file(content, filename)
        
        assert service.file_exists(file_path) is True
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_file_exists_returns_false_for_nonexistent_file(self):
        """Test that file_exists returns False for missing files"""
        service = StorageService()
        
        result = service.file_exists("/tmp/nonexistent_file_xyz.txt")
        
        assert result is False

    def test_delete_file_removes_file(self):
        """Test that delete_file removes the file"""
        service = StorageService()
        
        content = b"test content"
        filename = "test.txt"
        
        file_path = service.save_file(content, filename)
        assert os.path.exists(file_path)
        
        service.delete_file(file_path)
        
        assert os.path.exists(file_path) is False

    def test_get_file_content_reads_file_correctly(self):
        """Test that get_file_content reads file bytes"""
        service = StorageService()
        
        original_content = b"test file content 12345"
        filename = "test.bin"
        
        file_path = service.save_file(original_content, filename)
        
        retrieved_content = service.get_file_content(file_path)
        
        assert retrieved_content == original_content
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_generate_filename_creates_unique_names(self):
        """Test that generate_filename creates unique names"""
        service = StorageService()
        
        name1 = service.generate_filename("test.pdf")
        name2 = service.generate_filename("test.pdf")
        
        assert name1 != name2
        assert name1.endswith(".pdf")
        assert name2.endswith(".pdf")
