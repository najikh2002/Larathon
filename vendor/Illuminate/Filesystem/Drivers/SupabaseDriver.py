"""
Supabase Storage Driver
For serverless deployments using Supabase Storage
"""
from typing import Union, BinaryIO
import requests
import io


class SupabaseDriver:
    """Supabase Storage driver"""
    
    def __init__(self, config: dict):
        self.url = config.get("url")
        self.key = config.get("key")
        self.bucket = config.get("bucket", "larathon")
        self.visibility = config.get("visibility", "public")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY are required")
        
        self.storage_url = f"{self.url}/storage/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
        }
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure bucket exists, create if needed"""
        try:
            # Check if bucket exists
            response = requests.get(
                f"{self.storage_url}/bucket/{self.bucket}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                # Create bucket
                requests.post(
                    f"{self.storage_url}/bucket",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json={
                        "id": self.bucket,
                        "name": self.bucket,
                        "public": self.visibility == "public"
                    }
                )
        except Exception as e:
            print(f"Warning: Could not ensure bucket exists: {e}")
    
    def put(self, path: str, contents: Union[str, bytes, BinaryIO]) -> bool:
        """Store a file in Supabase Storage"""
        try:
            # Convert contents to bytes
            if isinstance(contents, str):
                file_data = contents.encode('utf-8')
                content_type = 'text/plain'
            elif isinstance(contents, bytes):
                file_data = contents
                content_type = 'application/octet-stream'
            else:  # File-like object
                file_data = contents.read()
                if isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
                content_type = 'application/octet-stream'
            
            # Detect content type from extension
            if path.endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.gif'):
                content_type = 'image/gif'
            elif path.endswith('.pdf'):
                content_type = 'application/pdf'
            
            # Remove leading slash
            path = path.lstrip('/')
            
            # Upload file
            response = requests.post(
                f"{self.storage_url}/object/{self.bucket}/{path}",
                headers={
                    **self.headers,
                    "Content-Type": content_type,
                },
                data=file_data
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            return False
    
    def get(self, path: str) -> bytes:
        """Get file contents from Supabase Storage"""
        path = path.lstrip('/')
        
        response = requests.get(
            f"{self.storage_url}/object/{self.bucket}/{path}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.content
        else:
            raise FileNotFoundError(f"File not found: {path}")
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        try:
            path = path.lstrip('/')
            response = requests.head(
                f"{self.storage_url}/object/{self.bucket}/{path}",
                headers=self.headers
            )
            return response.status_code == 200
        except:
            return False
    
    def delete(self, path: str) -> bool:
        """Delete a file"""
        try:
            path = path.lstrip('/')
            response = requests.delete(
                f"{self.storage_url}/object/{self.bucket}/{path}",
                headers=self.headers
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def url(self, path: str) -> str:
        """Get public URL for file"""
        path = path.lstrip('/')
        
        if self.visibility == "public":
            # Public URL
            return f"{self.storage_url}/object/public/{self.bucket}/{path}"
        else:
            # Signed URL (valid for 1 hour)
            return self._get_signed_url(path, 3600)
    
    def _get_signed_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate signed URL for private files"""
        try:
            response = requests.post(
                f"{self.storage_url}/object/sign/{self.bucket}/{path}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"expiresIn": expires_in}
            )
            
            if response.status_code == 200:
                data = response.json()
                return f"{self.url}{data['signedURL']}"
            else:
                # Fallback to regular URL
                return f"{self.storage_url}/object/{self.bucket}/{path}"
        except:
            return f"{self.storage_url}/object/{self.bucket}/{path}"
    
    def path(self, path: str) -> str:
        """Get 'path' (actually just returns URL for Supabase)"""
        return self.url(path)
    
    def files(self, directory: str = "") -> list:
        """List files in directory"""
        try:
            directory = directory.lstrip('/')
            
            response = requests.post(
                f"{self.storage_url}/object/list/{self.bucket}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={
                    "prefix": directory,
                    "limit": 100,
                    "offset": 0
                }
            )
            
            if response.status_code == 200:
                items = response.json()
                # Filter only files (not folders)
                return [item['name'] for item in items if item.get('metadata')]
            else:
                return []
        except:
            return []
    
    def directories(self, directory: str = "") -> list:
        """List directories"""
        try:
            directory = directory.lstrip('/')
            
            response = requests.post(
                f"{self.storage_url}/object/list/{self.bucket}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={
                    "prefix": directory,
                    "limit": 100,
                    "offset": 0
                }
            )
            
            if response.status_code == 200:
                items = response.json()
                # Filter only folders
                return [item['name'] for item in items if not item.get('metadata')]
            else:
                return []
        except:
            return []
