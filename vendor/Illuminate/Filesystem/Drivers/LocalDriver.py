"""
Local Filesystem Driver
For local development and testing
"""
import os
import shutil
from pathlib import Path
from typing import Union, BinaryIO


class LocalDriver:
    """Local filesystem driver"""
    
    def __init__(self, config: dict):
        self.root = config.get("root", "storage/app")
        self.url_prefix = config.get("url", "/storage")
        self.visibility = config.get("visibility", "private")
        
        # Ensure root directory exists
        Path(self.root).mkdir(parents=True, exist_ok=True)
    
    def put(self, path: str, contents: Union[str, bytes, BinaryIO]) -> bool:
        """Store a file"""
        try:
            full_path = self._full_path(path)
            
            # Create directory if needed
            Path(full_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            if isinstance(contents, str):
                with open(full_path, 'w') as f:
                    f.write(contents)
            elif isinstance(contents, bytes):
                with open(full_path, 'wb') as f:
                    f.write(contents)
            else:  # File-like object
                with open(full_path, 'wb') as f:
                    shutil.copyfileobj(contents, f)
            
            return True
        except Exception as e:
            print(f"Error storing file: {e}")
            return False
    
    def get(self, path: str) -> bytes:
        """Get file contents"""
        full_path = self._full_path(path)
        with open(full_path, 'rb') as f:
            return f.read()
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(self._full_path(path))
    
    def delete(self, path: str) -> bool:
        """Delete a file"""
        try:
            full_path = self._full_path(path)
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def url(self, path: str) -> str:
        """Get public URL for file"""
        # For local development, return URL that can be served
        return f"{self.url_prefix}/{path}"
    
    def path(self, path: str) -> str:
        """Get full filesystem path"""
        return self._full_path(path)
    
    def files(self, directory: str = "") -> list:
        """List files in directory"""
        full_path = self._full_path(directory)
        
        if not os.path.exists(full_path):
            return []
        
        result = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isfile(item_path):
                # Return relative path
                rel_path = os.path.join(directory, item) if directory else item
                result.append(rel_path)
        
        return result
    
    def directories(self, directory: str = "") -> list:
        """List directories"""
        full_path = self._full_path(directory)
        
        if not os.path.exists(full_path):
            return []
        
        result = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                rel_path = os.path.join(directory, item) if directory else item
                result.append(rel_path)
        
        return result
    
    def size(self, path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(self._full_path(path))
    
    def _full_path(self, path: str) -> str:
        """Get full filesystem path"""
        # Remove leading slashes
        path = path.lstrip('/')
        return os.path.join(self.root, path)
