"""
S3-Compatible Driver
Universal driver for all S3-compatible storage services:
- AWS S3
- Cloudflare R2
- MinIO
- DigitalOcean Spaces
- Wasabi
- Backblaze B2
- Supabase Storage (S3 mode)
- Any S3-compatible object storage
"""
from typing import Union, BinaryIO


class S3Driver:
    """
    Universal S3-compatible storage driver
    
    Supports any S3-compatible object storage service by providing
    the appropriate endpoint URL and credentials.
    """
    
    def __init__(self, config: dict):
        self.key = config.get("key")
        self.secret = config.get("secret")
        self.region = config.get("region", "auto")
        self.bucket = config.get("bucket")
        self.endpoint = config.get("endpoint")
        self.url = config.get("url")
        self.visibility = config.get("visibility", "public")
        self.use_path_style = config.get("use_path_style", False)  # For MinIO compatibility
        
        if not self.key or not self.secret or not self.bucket:
            raise ValueError("S3 credentials (key, secret) and bucket are required")
        
        # Initialize boto3 client
        try:
            import boto3
            from botocore.config import Config
            
            # Configure boto3
            boto_config = Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path' if self.use_path_style else 'auto'}
            )
            
            # Create S3 client
            client_kwargs = {
                'service_name': 's3',
                'aws_access_key_id': self.key,
                'aws_secret_access_key': self.secret,
                'config': boto_config
            }
            
            # Add endpoint if provided (for non-AWS S3)
            if self.endpoint:
                client_kwargs['endpoint_url'] = self.endpoint
            
            # Add region
            if self.region and self.region != 'auto':
                client_kwargs['region_name'] = self.region
            
            self.client = boto3.client(**client_kwargs)
            
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 driver.\n"
                "Install: pip install boto3\n"
                "Add to requirements.txt: boto3==1.34.0"
            )
    
    def put(self, path: str, contents: Union[str, bytes, BinaryIO]) -> bool:
        """Store a file in S3"""
        try:
            path = path.lstrip('/')
            
            # Convert contents to bytes
            if isinstance(contents, str):
                file_data = contents.encode('utf-8')
            elif isinstance(contents, bytes):
                file_data = contents
            else:  # File-like object
                file_data = contents.read()
                if isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
            
            # Detect content type
            content_type = self._get_content_type(path)
            
            # Upload
            self.client.put_object(
                Bucket=self.bucket,
                Key=path,
                Body=file_data,
                ContentType=content_type,
                ACL='public-read' if self.visibility == 'public' else 'private'
            )
            
            return True
            
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False
    
    def get(self, path: str) -> bytes:
        """Get file contents"""
        path = path.lstrip('/')
        
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=path
        )
        
        return response['Body'].read()
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        try:
            path = path.lstrip('/')
            self.client.head_object(
                Bucket=self.bucket,
                Key=path
            )
            return True
        except:
            return False
    
    def delete(self, path: str) -> bool:
        """Delete a file"""
        try:
            path = path.lstrip('/')
            self.client.delete_object(
                Bucket=self.bucket,
                Key=path
            )
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def url(self, path: str) -> str:
        """Get public URL for file"""
        path = path.lstrip('/')
        
        if self.url:
            # Custom public URL
            return f"{self.url}/{path}"
        elif self.endpoint:
            # Endpoint-based URL
            return f"{self.endpoint}/{self.bucket}/{path}"
        else:
            # AWS S3 URL
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{path}"
    
    def path(self, path: str) -> str:
        """Get 'path' (returns URL for S3)"""
        return self.url(path)
    
    def files(self, directory: str = "") -> list:
        """List files in directory"""
        try:
            directory = directory.lstrip('/')
            if directory and not directory.endswith('/'):
                directory += '/'
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=directory,
                Delimiter='/'
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            else:
                return []
        except:
            return []
    
    def directories(self, directory: str = "") -> list:
        """List directories"""
        try:
            directory = directory.lstrip('/')
            if directory and not directory.endswith('/'):
                directory += '/'
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=directory,
                Delimiter='/'
            )
            
            if 'CommonPrefixes' in response:
                return [prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']]
            else:
                return []
        except:
            return []
    
    def _get_content_type(self, path: str) -> str:
        """Detect content type from file extension"""
        if path.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif path.endswith('.png'):
            return 'image/png'
        elif path.endswith('.gif'):
            return 'image/gif'
        elif path.endswith('.pdf'):
            return 'application/pdf'
        elif path.endswith('.txt'):
            return 'text/plain'
        elif path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        else:
            return 'application/octet-stream'
