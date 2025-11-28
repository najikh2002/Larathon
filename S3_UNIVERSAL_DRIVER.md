# Universal S3 Driver - Support All S3-Compatible Storage

## Overview

Larathon's **Universal S3 Driver** supports **ANY** S3-compatible object storage service through a single, generalized driver. No need for separate drivers for each service!

## Supported Services

✅ **AWS S3** - Original Amazon S3
✅ **Cloudflare R2** - Zero egress fees
✅ **MinIO** - Self-hosted, open-source
✅ **DigitalOcean Spaces** - Easy & affordable
✅ **Wasabi** - Hot cloud storage, cheap
✅ **Backblaze B2** - Affordable cloud storage
✅ **Supabase Storage** - (via S3-compatible mode)
✅ **Any other S3-compatible service**

## Why Universal S3?

### Before (Specific Drivers):
```python
# Need separate driver for each service
R2Driver
MinIODriver  
SpacesDriver
WasabiDriver
# ... one driver per service
```

### After (Universal Driver):
```python
# ONE driver for ALL S3-compatible services!
S3Driver
# Just configure endpoint & credentials
```

## How It Works

All S3-compatible services use the same API (Amazon S3 protocol), but with different:
- **Endpoints** - Where the service is hosted
- **Credentials** - Access keys
- **Regions** - Geographic location (some services use "auto")
- **Configuration** - Minor differences (e.g., MinIO uses path-style addressing)

The Universal S3 Driver handles all these differences through configuration!

## Configuration Examples

### 1. AWS S3 (Original)

**.env**
```bash
FILESYSTEM_DISK=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=larathon
AWS_URL=https://cdn.yourdomain.com  # Optional: CloudFront CDN
```

**config/filesystems.py**
```python
"s3": {
    "driver": "s3",
    "key": os.getenv("AWS_ACCESS_KEY_ID"),
    "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    "bucket": os.getenv("AWS_BUCKET"),
    "url": os.getenv("AWS_URL"),
    "visibility": "public",
}
```

### 2. Cloudflare R2

**Features**: Zero egress fees, S3-compatible, custom domains

**.env**
```bash
FILESYSTEM_DISK=r2
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=larathon
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://files.yourdomain.com
```

**config/filesystems.py**
```python
"r2": {
    "driver": "s3",
    "key": os.getenv("R2_ACCESS_KEY_ID"),
    "secret": os.getenv("R2_SECRET_ACCESS_KEY"),
    "region": "auto",  # R2 uses auto region
    "bucket": os.getenv("R2_BUCKET"),
    "endpoint": os.getenv("R2_ENDPOINT"),
    "url": os.getenv("R2_PUBLIC_URL"),
    "visibility": "public",
}
```

### 3. MinIO (Self-hosted)

**Features**: Open-source, self-hosted, full S3 compatibility

**.env**
```bash
FILESYSTEM_DISK=minio
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=larathon
MINIO_ENDPOINT=http://localhost:9000
MINIO_PUBLIC_URL=http://localhost:9000/larathon
```

**config/filesystems.py**
```python
"minio": {
    "driver": "s3",
    "key": os.getenv("MINIO_ACCESS_KEY"),
    "secret": os.getenv("MINIO_SECRET_KEY"),
    "region": "us-east-1",
    "bucket": os.getenv("MINIO_BUCKET"),
    "endpoint": os.getenv("MINIO_ENDPOINT"),
    "url": os.getenv("MINIO_PUBLIC_URL"),
    "use_path_style": True,  # MinIO requires this!
    "visibility": "public",
}
```

**Docker Compose for MinIO**:
```yaml
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
```

### 4. DigitalOcean Spaces

**Features**: Simple, affordable, includes CDN

**.env**
```bash
FILESYSTEM_DISK=spaces
SPACES_ACCESS_KEY=your-spaces-access-key
SPACES_SECRET_KEY=your-spaces-secret-key
SPACES_REGION=nyc3  # or sgp1, fra1, ams3, etc.
SPACES_BUCKET=larathon
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
SPACES_URL=https://larathon.nyc3.cdn.digitaloceanspaces.com
```

**config/filesystems.py**
```python
"spaces": {
    "driver": "s3",
    "key": os.getenv("SPACES_ACCESS_KEY"),
    "secret": os.getenv("SPACES_SECRET_KEY"),
    "region": os.getenv("SPACES_REGION", "nyc3"),
    "bucket": os.getenv("SPACES_BUCKET"),
    "endpoint": os.getenv("SPACES_ENDPOINT"),
    "url": os.getenv("SPACES_URL"),  # CDN URL
    "visibility": "public",
}
```

### 5. Wasabi

**Features**: Hot cloud storage, low cost, no egress fees

**.env**
```bash
FILESYSTEM_DISK=wasabi
WASABI_ACCESS_KEY=your-access-key
WASABI_SECRET_KEY=your-secret-key
WASABI_REGION=us-east-1  # or us-west-1, eu-central-1
WASABI_BUCKET=larathon
WASABI_ENDPOINT=https://s3.wasabisys.com
WASABI_URL=https://s3.wasabisys.com/larathon
```

**config/filesystems.py**
```python
"wasabi": {
    "driver": "s3",
    "key": os.getenv("WASABI_ACCESS_KEY"),
    "secret": os.getenv("WASABI_SECRET_KEY"),
    "region": os.getenv("WASABI_REGION", "us-east-1"),
    "bucket": os.getenv("WASABI_BUCKET"),
    "endpoint": os.getenv("WASABI_ENDPOINT"),
    "url": os.getenv("WASABI_URL"),
    "visibility": "public",
}
```

### 6. Backblaze B2

**Features**: Affordable, S3-compatible API

**.env**
```bash
FILESYSTEM_DISK=b2
B2_ACCESS_KEY=your-key-id
B2_SECRET_KEY=your-application-key
B2_REGION=us-west-002  # Check your bucket region
B2_BUCKET=larathon
B2_ENDPOINT=https://s3.us-west-002.backblazeb2.com
B2_URL=https://f002.backblazeb2.com/file/larathon
```

**config/filesystems.py**
```python
"b2": {
    "driver": "s3",
    "key": os.getenv("B2_ACCESS_KEY"),
    "secret": os.getenv("B2_SECRET_KEY"),
    "region": os.getenv("B2_REGION", "us-west-002"),
    "bucket": os.getenv("B2_BUCKET"),
    "endpoint": os.getenv("B2_ENDPOINT"),
    "url": os.getenv("B2_URL"),
    "visibility": "public",
}
```

## Usage (Same for All Services!)

```python
from vendor.Illuminate.Filesystem.Storage import Storage

# Store file (works with ANY configured S3 service)
Storage.put("uploads/photo.jpg", file_contents)

# Get URL
url = Storage.url("uploads/photo.jpg")
# AWS S3: https://larathon.s3.amazonaws.com/uploads/photo.jpg
# R2: https://files.yourdomain.com/uploads/photo.jpg
# MinIO: http://localhost:9000/larathon/uploads/photo.jpg

# Same API for all operations!
Storage.get("uploads/photo.jpg")
Storage.exists("uploads/photo.jpg")
Storage.delete("uploads/photo.jpg")
Storage.files("uploads")
```

## Requirements

Install boto3 (AWS SDK for Python):

```bash
pip install boto3
```

Add to `requirements.txt`:
```
boto3==1.34.0
```

## Switching Services

**Just change environment variables** - code stays the same!

```bash
# Development: Use MinIO locally
FILESYSTEM_DISK=minio

# Production: Switch to Cloudflare R2
FILESYSTEM_DISK=r2

# Or AWS S3
FILESYSTEM_DISK=s3
```

**Your code doesn't change at all!**

## Configuration Options

All S3-compatible services support these options:

| Option | Required | Description |
|--------|----------|-------------|
| `key` | ✅ | Access key ID |
| `secret` | ✅ | Secret access key |
| `region` | ✅ | Region (use "auto" for services like R2) |
| `bucket` | ✅ | Bucket name |
| `endpoint` | ⚠️ | Service endpoint (required for non-AWS) |
| `url` | ⬜ | Public URL/CDN |
| `use_path_style` | ⬜ | Path-style addressing (for MinIO) |
| `visibility` | ⬜ | Default visibility (public/private) |

## Special Configurations

### MinIO - Path-Style Addressing

MinIO requires `use_path_style: True`:

```python
"minio": {
    "driver": "s3",
    # ... other config
    "use_path_style": True,  # Required for MinIO!
}
```

### Custom Domains / CDN

Set `url` parameter for custom domains:

```python
"r2": {
    "driver": "s3",
    # ... other config
    "url": "https://files.yourdomain.com",  # Custom domain
}
```

Then `Storage.url()` returns:
```
https://files.yourdomain.com/uploads/photo.jpg
```

Instead of:
```
https://<account-id>.r2.cloudflarestorage.com/uploads/photo.jpg
```

## Cost Comparison

| Service | Storage | Egress | Best For |
|---------|---------|--------|----------|
| **AWS S3** | $0.023/GB | $0.09/GB | Enterprise, full features |
| **Cloudflare R2** | $0.015/GB | **FREE** ✨ | High traffic, bandwidth-heavy |
| **MinIO** | Self-hosted | Self-hosted | On-premise, full control |
| **DO Spaces** | $5/month (250GB) | 1TB included | Simple pricing |
| **Wasabi** | $5.99/TB | **FREE** ✨ | Hot storage, large files |
| **Backblaze B2** | $0.005/GB | $0.01/GB | Archive, backup, affordable |

## Recommendation by Use Case

### Serverless Deployment (Vercel, etc.)
**Choose**: Cloudflare R2 or Supabase Storage
**Why**: Zero egress fees, good free tier, fast

### High Bandwidth / Video
**Choose**: Cloudflare R2 or Wasabi  
**Why**: Free egress, cost-effective for large files

### Development / Testing
**Choose**: MinIO (self-hosted)
**Why**: Free, full S3 compatibility, runs locally

### Enterprise / Full Features
**Choose**: AWS S3
**Why**: Most mature, extensive features, global

### Budget-Conscious
**Choose**: Backblaze B2 or DigitalOcean Spaces
**Why**: Lowest storage costs, predictable pricing

## Migration Between Services

**Example: Moving from MinIO (dev) to R2 (prod)**

1. **Development** (.env.local):
```bash
FILESYSTEM_DISK=minio
MINIO_ENDPOINT=http://localhost:9000
# ... other MinIO config
```

2. **Production** (.env.production):
```bash
FILESYSTEM_DISK=r2
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
# ... other R2 config
```

3. **Code**: No changes needed!
```python
# This works with both MinIO and R2
Storage.put("files/document.pdf", contents)
```

## Summary

✅ **One driver for all S3-compatible services**
✅ **Same code, different storage backend**
✅ **Easy switching via environment variables**
✅ **Support for AWS S3, R2, MinIO, Spaces, Wasabi, B2, and more**
✅ **Automatic handling of service-specific requirements**
✅ **Cost flexibility** - choose based on your needs

**Universal compatibility = Maximum flexibility!** 🚀
