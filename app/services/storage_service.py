import os
import uuid
from pathlib import Path
from typing import Optional


class StorageService:
    """Service for managing file storage"""
    
    def __init__(self, storage_dir: str = "/tmp/notebookum_uploads"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename"""
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"
    
    def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return full path"""
        unique_filename = self.generate_filename(filename)
        file_path = self.storage_dir / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return Path(file_path).exists()
    
    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Read file content"""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
