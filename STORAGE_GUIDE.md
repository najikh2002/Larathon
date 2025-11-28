# Storage System Guide - Larathon

## Overview

Larathon includes a flexible, Laravel-inspired storage system that supports multiple drivers:
- **Local Storage** - For development
- **Supabase Storage** - For serverless deployments
- **Cloudflare R2** - S3-compatible object storage
- **AWS S3** - Full S3 support (using same driver as R2)

The storage system provides a unified API regardless of the underlying storage driver, making it easy to switch between local development and production cloud storage.

## Why External Storage for Serverless?

Serverless environments (like Vercel) have **ephemeral filesystems**:
- Files uploaded during a request are **lost** after the function finishes
- Each function invocation may run on a different server
- No persistent local storage between requests

**Solution**: Use external object storage (Supabase/R2/S3) that persists files independently of your serverless functions.

## Architecture

```
Local Development          Production (Serverless)
─────────────────          ────────────────────────
┌─────────────┐           ┌──────────────────┐
│   FastAPI   │           │  Vercel Function │
│   (local)   │           │   (serverless)   │
└──────┬──────┘           └────────┬─────────┘
       │                            │
       │ Storage                    │ Storage
       │ Facade                     │ Facade
       │                            │
┌──────▼──────────┐        ┌───────▼──────────┐
│  Local Driver   │        │ Supabase Driver  │
│  storage/app/   │        │  (Cloud Storage) │
└─────────────────┘        └──────────────────┘
```

## Configuration

### 1. Environment Variables

**Development (.env)**:
```bash
FILESYSTEM_DISK=local
```

**Production (.env)**:
```bash
# Supabase Storage
FILESYSTEM_DISK=supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=larathon

# OR Cloudflare R2
# FILESYSTEM_DISK=r2
# R2_ACCESS_KEY_ID=your-access-key
# R2_SECRET_ACCESS_KEY=your-secret-key
# R2_BUCKET=larathon
# R2_ENDPOINT=https://xxxxxxxxxxxxx.r2.cloudflarestorage.com
# R2_PUBLIC_URL=https://your-domain.com
```

### 2. Config File

File: `config/filesystems.py`

```python
disks = {
    "local": {
        "driver": "local",
        "root": "storage/app",
        "url": "/storage",
    },
    
    "supabase": {
        "driver": "supabase",
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY"),
        "bucket": os.getenv("SUPABASE_BUCKET", "larathon"),
    },
    
    "r2": {
        "driver": "s3",
        "key": os.getenv("R2_ACCESS_KEY_ID"),
        "secret": os.getenv("R2_SECRET_ACCESS_KEY"),
        "bucket": os.getenv("R2_BUCKET"),
        "endpoint": os.getenv("R2_ENDPOINT"),
    },
}
```

## Usage Examples

### Basic Operations

```python
from vendor.Illuminate.Filesystem.Storage import Storage

# Store a file
Storage.put("uploads/photo.jpg", file_contents)

# Get file contents
contents = Storage.get("uploads/photo.jpg")

# Check if file exists
if Storage.exists("uploads/photo.jpg"):
    print("File exists!")

# Delete a file
Storage.delete("uploads/photo.jpg")

# Get public URL
url = Storage.url("uploads/photo.jpg")
# Returns: https://xxxxx.supabase.co/storage/v1/object/public/larathon/uploads/photo.jpg
```

### Using Different Disks

```python
# Use specific disk
Storage.disk("supabase").put("file.jpg", contents)
Storage.disk("local").put("file.jpg", contents)

# Default disk (from FILESYSTEM_DISK env)
Storage.put("file.jpg", contents)
```

### File Upload Example

```python
from app.Http.Controllers.Controller import Controller
from vendor.Illuminate.Support.Helpers.storage import upload_file, get_file_url

class UploadController(Controller):
    async def upload(self, request):
        # Get uploaded file from form
        form = await request.form()
        file = form["file"]
        
        # Upload to storage
        path = upload_file(file, directory="uploads")
        
        # Get public URL
        url = get_file_url(path)
        
        return {"success": True, "url": url, "path": path}
```

### Helper Functions

```python
from vendor.Illuminate.Support.Helpers.storage import (
    upload_file,
    get_file_url,
    delete_file,
    file_exists
)

# Upload file
path = upload_file(file, directory="avatars", disk="supabase")

# Get URL
url = get_file_url(path)

# Check existence
if file_exists(path):
    delete_file(path)
```

## Storage Drivers

### Local Driver

**Best for**: Development, testing

**Location**: `storage/app/`

**URLs**: `/storage/filename`

```python
# .env
FILESYSTEM_DISK=local

# Usage
Storage.put("test.txt", "Hello World")
# Stored at: storage/app/test.txt
```

### Supabase Storage Driver

**Best for**: Serverless deployments, production

**Setup**:
1. Create project at [supabase.com](https://supabase.com)
2. Go to Storage → Create bucket → Name it "larathon"
3. Set bucket to "Public" (for public files)
4. Get credentials from Settings → API

```python
# .env
FILESYSTEM_DISK=supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=larathon

# Usage
Storage.put("uploads/photo.jpg", file_data)
# URL: https://xxxxx.supabase.co/storage/v1/object/public/larathon/uploads/photo.jpg
```

**Features**:
- ✅ Automatic bucket creation
- ✅ Public URLs for public buckets
- ✅ Signed URLs for private buckets
- ✅ Built-in CDN
- ✅ Image transformations (via URL params)

### Cloudflare R2 Driver

**Best for**: Large files, high bandwidth, cost-effective

**Setup**:
1. Go to Cloudflare Dashboard → R2
2. Create bucket
3. Create API Token (R2 Manage R2 API Tokens)
4. Get Account ID and bucket name

```python
# .env
FILESYSTEM_DISK=r2
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=yyyyyyyyyyyyyyyyyyyy
R2_BUCKET=larathon
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://files.yourdomain.com  # Custom domain

# Usage
Storage.put("videos/demo.mp4", video_data)
# URL: https://files.yourdomain.com/videos/demo.mp4
```

**Requires**: `pip install boto3`

## Example: Image Upload System

### Controller

```python
from app.Http.Controllers.Controller import Controller
from vendor.Illuminate.Filesystem.Storage import Storage

class ImageController(Controller):
    def index(self, request):
        # List all uploaded images
        files = Storage.files("uploads")
        
        images = []
        for file_path in files:
            images.append({
                'path': file_path,
                'url': Storage.url(file_path),
                'name': file_path.split('/')[-1]
            })
        
        return self.view("images.index", request, {"images": images})
    
    async def upload(self, request):
        form = await request.form()
        file = form["image"]
        
        # Generate unique filename
        import os
        from datetime import datetime
        name, ext = os.path.splitext(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{name}_{timestamp}{ext}"
        
        # Store in uploads directory
        path = f"uploads/{filename}"
        Storage.put(path, file.file)
        
        return self.redirect("/images")
    
    def delete(self, request, path):
        Storage.delete(path)
        return self.redirect("/images")
```

### Template (images/index.html)

```html
<form action="/images/upload" method="POST" enctype="multipart/form-data">
    <input type="file" name="image" accept="image/*" required>
    <button type="submit">Upload</button>
</form>

<div class="images">
    {% for image in images %}
    <div class="image-card">
        <img src="{{ image.url }}" alt="{{ image.name }}">
        <button onclick="deleteImage('{{ image.path }}')">Delete</button>
    </div>
    {% endfor %}
</div>
```

## Switching Between Storage Drivers

The beauty of this system: **Just change one environment variable!**

**Development**:
```bash
FILESYSTEM_DISK=local
```

**Production**:
```bash
FILESYSTEM_DISK=supabase  # or r2
```

Your code remains the same - the storage driver handles the rest.

## Testing the Storage System

Visit: `http://localhost:8000/storage`

This page demonstrates:
- File upload form
- Listing uploaded files
- Displaying files from storage
- Deleting files
- Works with any configured driver

## Best Practices

### 1. Organize Files by Type

```python
Storage.put("avatars/user123.jpg", avatar)
Storage.put("documents/invoice.pdf", doc)
Storage.put("uploads/photo.jpg", photo)
```

### 2. Generate Unique Filenames

```python
from datetime import datetime
import os

def generate_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{name}_{timestamp}{ext}"
```

### 3. Validate File Types

```python
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

def is_allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
```

### 4. Handle Errors Gracefully

```python
try:
    Storage.put(path, contents)
except Exception as e:
    print(f"Upload failed: {e}")
    return {"error": "Upload failed"}
```

### 5. Clean Up Old Files

```python
def cleanup_old_uploads():
    files = Storage.files("temp")
    for file in files:
        # Delete files older than 24 hours
        if is_old(file):
            Storage.delete(file)
```

## Deployment Notes

### For Vercel

1. Set environment variables in Vercel Dashboard:
   ```
   FILESYSTEM_DISK=supabase
   SUPABASE_URL=...
   SUPABASE_KEY=...
   SUPABASE_BUCKET=larathon
   ```

2. Files automatically sync to Supabase Storage
3. URLs work immediately (no local filesystem needed)

### For Local Development

1. Use `FILESYSTEM_DISK=local`
2. Files stored in `storage/app/`
3. Commit `.gitkeep` files, not actual uploads
4. `.gitignore` excludes `storage/app/*`

## Troubleshooting

### Files Not Persisting

**Problem**: Files disappear after deployment

**Solution**: Make sure `FILESYSTEM_DISK=supabase` (or r2) in production, not `local`

### 403 Forbidden Errors

**Problem**: Can't access files via URL

**Solution**: 
- Supabase: Set bucket to "Public" in Storage settings
- R2: Configure custom domain with public access

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'boto3'`

**Solution**: For R2/S3 driver:
```bash
pip install boto3
```

Add to `requirements.txt`:
```
boto3==1.34.0
```

## Summary

**Local Development**:
- ✅ Use local driver
- ✅ Files in `storage/app/`
- ✅ Fast, no external dependencies

**Production/Serverless**:
- ✅ Use Supabase or R2 driver
- ✅ Files persist independently
- ✅ Public URLs for serving
- ✅ No filesystem limitations

**One codebase, multiple storage options** - just change the environment variable! 🚀
