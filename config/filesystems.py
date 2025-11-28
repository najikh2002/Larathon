"""
Filesystem Configuration
Laravel-style storage configuration for multiple storage drivers
"""
import os

# Default filesystem disk
default = os.getenv("FILESYSTEM_DISK", "local")

# Filesystem disks configuration
disks = {
    # ==========================================
    # Local Storage (Development)
    # ==========================================
    "local": {
        "driver": "local",
        "root": os.path.join(os.getcwd(), "storage", "app"),
        "url": "/storage",
        "visibility": "private",
    },
    
    "public": {
        "driver": "local",
        "root": os.path.join(os.getcwd(), "storage", "app", "public"),
        "url": "/storage",
        "visibility": "public",
    },
    
    # ==========================================
    # Supabase Storage (Recommended for Serverless)
    # ==========================================
    "supabase": {
        "driver": "supabase",
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY"),
        "bucket": os.getenv("SUPABASE_BUCKET", "larathon"),
        "visibility": "public",
    },
    
    # ==========================================
    # S3-Compatible Storage
    # Universal driver for all S3-compatible services
    # ==========================================
    
    # AWS S3 (Original)
    "s3": {
        "driver": "s3",
        "key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        "bucket": os.getenv("AWS_BUCKET"),
        "url": os.getenv("AWS_URL"),  # CloudFront URL if using CDN
        "visibility": "public",
    },
    
    # Cloudflare R2
    "r2": {
        "driver": "s3",
        "key": os.getenv("R2_ACCESS_KEY_ID"),
        "secret": os.getenv("R2_SECRET_ACCESS_KEY"),
        "region": "auto",  # R2 uses auto region
        "bucket": os.getenv("R2_BUCKET"),
        "endpoint": os.getenv("R2_ENDPOINT"),
        "url": os.getenv("R2_PUBLIC_URL"),  # Custom domain
        "visibility": "public",
    },
    
    # MinIO (Self-hosted S3)
    "minio": {
        "driver": "s3",
        "key": os.getenv("MINIO_ACCESS_KEY"),
        "secret": os.getenv("MINIO_SECRET_KEY"),
        "region": "us-east-1",
        "bucket": os.getenv("MINIO_BUCKET"),
        "endpoint": os.getenv("MINIO_ENDPOINT"),  # e.g., http://minio:9000
        "url": os.getenv("MINIO_PUBLIC_URL"),
        "use_path_style": True,  # MinIO requires path-style addressing
        "visibility": "public",
    },
    
    # DigitalOcean Spaces
    "spaces": {
        "driver": "s3",
        "key": os.getenv("SPACES_ACCESS_KEY"),
        "secret": os.getenv("SPACES_SECRET_KEY"),
        "region": os.getenv("SPACES_REGION", "nyc3"),
        "bucket": os.getenv("SPACES_BUCKET"),
        "endpoint": os.getenv("SPACES_ENDPOINT"),  # e.g., https://nyc3.digitaloceanspaces.com
        "url": os.getenv("SPACES_URL"),  # CDN URL
        "visibility": "public",
    },
    
    # Wasabi
    "wasabi": {
        "driver": "s3",
        "key": os.getenv("WASABI_ACCESS_KEY"),
        "secret": os.getenv("WASABI_SECRET_KEY"),
        "region": os.getenv("WASABI_REGION", "us-east-1"),
        "bucket": os.getenv("WASABI_BUCKET"),
        "endpoint": os.getenv("WASABI_ENDPOINT"),  # e.g., https://s3.wasabisys.com
        "url": os.getenv("WASABI_URL"),
        "visibility": "public",
    },
    
    # Backblaze B2
    "b2": {
        "driver": "s3",
        "key": os.getenv("B2_ACCESS_KEY"),
        "secret": os.getenv("B2_SECRET_KEY"),
        "region": os.getenv("B2_REGION", "us-west-002"),
        "bucket": os.getenv("B2_BUCKET"),
        "endpoint": os.getenv("B2_ENDPOINT"),  # e.g., https://s3.us-west-002.backblazeb2.com
        "url": os.getenv("B2_URL"),
        "visibility": "public",
    },
}

# Symbolic links (for serving public storage)
links = {
    "public/storage": "storage/app/public"
}
