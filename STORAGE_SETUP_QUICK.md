# Quick Start - Storage System

## What Was Built

A complete storage system that works both locally (development) and with external object storage (production/serverless).

## Architecture

```
┌─────────────────────────────────────────┐
│         Storage Facade                  │
│  (Unified API for all operations)       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼─────┐  ┌─────▼────────┐  ┌──────▼─────┐
│   Local    │  │  Supabase    │  │  R2/S3     │
│  Driver    │  │   Driver     │  │   Driver   │
└────────────┘  └──────────────┘  └────────────┘
   storage/       Supabase Cloud   Cloudflare R2
     app/          Storage           AWS S3
```

## Files Created

### Core System
```
config/
├── filesystems.py                    # Storage configuration

vendor/Illuminate/Filesystem/
├── Storage.py                        # Storage Facade
├── Drivers/
│   ├── LocalDriver.py               # Local filesystem
│   ├── SupabaseDriver.py            # Supabase Storage
│   └── S3Driver.py                  # R2/S3 compatible

vendor/Illuminate/Support/Helpers/
└── storage.py                        # Helper functions
```

### Example Implementation
```
app/Http/Controllers/
└── StorageController.py              # Upload/list/delete demo

resources/views/storage/
└── index.html                        # File manager UI

routes/
└── web.py                           # Storage routes
```

### Storage Directory
```
storage/
└── app/
    ├── .gitkeep                     # Preserve in git
    └── public/
        └── .gitkeep                 # Preserve in git
```

## Quick Usage

### 1. Development (Local Storage)

**.env**
```bash
FILESYSTEM_DISK=local
```

**Upload a file**:
```python
from vendor.Illuminate.Filesystem.Storage import Storage

# Store file
Storage.put("uploads/photo.jpg", file_contents)

# Get URL
url = Storage.url("uploads/photo.jpg")
# Returns: /storage/uploads/photo.jpg
```

### 2. Production (Supabase)

**.env**
```bash
FILESYSTEM_DISK=supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=larathon
```

**Same code, different storage**:
```python
# Same API!
Storage.put("uploads/photo.jpg", file_contents)

# Get public URL
url = Storage.url("uploads/photo.jpg")
# Returns: https://xxxxx.supabase.co/storage/v1/object/public/larathon/uploads/photo.jpg
```

## Test It

### 1. Start Server
```bash
python artisan.py serve
```

### 2. Visit Storage Demo
```
http://localhost:8000/storage
```

### 3. Upload a File
- Click "Upload File"
- Select an image
- Click Upload
- See it in the list with a public URL

### 4. View/Delete Files
- Click "View" to open image in new tab
- Click "Delete" to remove from storage

## Setup for Production

### Option 1: Supabase Storage (Recommended)

**Step 1**: Create Supabase Project
- Go to [supabase.com](https://supabase.com)
- Create new project

**Step 2**: Create Storage Bucket
- Dashboard → Storage → New Bucket
- Name: `larathon`
- Make it Public

**Step 3**: Get Credentials
- Settings → API
- Copy:
  - Project URL (`SUPABASE_URL`)
  - Anon public key (`SUPABASE_KEY`)

**Step 4**: Update .env
```bash
FILESYSTEM_DISK=supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=larathon
```

**Step 5**: Test
```python
from vendor.Illuminate.Filesystem.Storage import Storage

Storage.put("test.txt", "Hello Supabase!")
print(Storage.url("test.txt"))
# https://xxxxx.supabase.co/storage/v1/object/public/larathon/test.txt
```

### Option 2: Cloudflare R2

**Step 1**: Create R2 Bucket
- Cloudflare Dashboard → R2
- Create bucket: `larathon`

**Step 2**: Create API Token
- R2 → Manage R2 API Tokens
- Create token with read/write permissions

**Step 3**: Update .env
```bash
FILESYSTEM_DISK=r2
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET=larathon
R2_ENDPOINT=https://xxxxxxxxxxxxx.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://files.yourdomain.com
```

**Step 4**: Install boto3
```bash
pip install boto3
```

Add to `requirements.txt`:
```
boto3==1.34.0
```

## Code Examples

### Upload File in Controller
```python
from vendor.Illuminate.Support.Helpers.storage import upload_file

class MyController(Controller):
    async def upload(self, request):
        form = await request.form()
        file = form["avatar"]
        
        # Upload to storage
        path = upload_file(file, directory="avatars")
        
        # Get URL
        from vendor.Illuminate.Support.Helpers.storage import get_file_url
        url = get_file_url(path)
        
        return {"success": True, "url": url}
```

### Display Image in Template
```html
<img src="{{ image_url }}" alt="User Avatar">
```

Where `image_url` comes from:
```python
from vendor.Illuminate.Filesystem.Storage import Storage

def show_profile(request, user_id):
    # Get user's avatar path from database
    avatar_path = "avatars/user123.jpg"
    
    # Get public URL
    avatar_url = Storage.url(avatar_path)
    
    return self.view("profile", request, {
        "avatar_url": avatar_url
    })
```

## Switching Storage Drivers

**The beauty**: Just change one environment variable!

**Development**:
```bash
FILESYSTEM_DISK=local
```

**Production**:
```bash
FILESYSTEM_DISK=supabase  # or r2
```

**Your code stays exactly the same!**

## Common Operations

### Store File
```python
Storage.put("path/file.jpg", contents)
```

### Get File
```python
contents = Storage.get("path/file.jpg")
```

### Check Exists
```python
if Storage.exists("path/file.jpg"):
    print("File exists")
```

### Delete File
```python
Storage.delete("path/file.jpg")
```

### Get URL
```python
url = Storage.url("path/file.jpg")
```

### List Files
```python
files = Storage.files("uploads")  # List files in uploads/
```

### Use Specific Disk
```python
Storage.disk("supabase").put("file.jpg", contents)
Storage.disk("local").put("file.jpg", contents)
```

## Deployment Checklist

- [ ] Set `FILESYSTEM_DISK=supabase` (or `r2`) in Vercel environment variables
- [ ] Add Supabase credentials to Vercel
- [ ] Create and configure Supabase bucket
- [ ] Test upload via `/storage` page
- [ ] Verify files persist after deployment
- [ ] Check public URLs work

## Troubleshooting

**Problem**: Files disappear after deployment
**Solution**: Using `local` driver in serverless won't work. Use `supabase` or `r2`.

**Problem**: Can't access uploaded files
**Solution**: Make sure Supabase bucket is set to "Public" or generate signed URLs.

**Problem**: Import error: `boto3`
**Solution**: Only needed for R2/S3. Run: `pip install boto3`

## Summary

✅ **Multiple storage drivers** - Local, Supabase, R2/S3
✅ **Unified API** - Same code works everywhere  
✅ **Serverless ready** - Files persist in cloud
✅ **Easy switching** - Just change env variable
✅ **Helper functions** - Simplified operations
✅ **Example UI** - Working file manager at `/storage`

**One codebase, infinite storage options!** 🚀

For complete documentation, see: `STORAGE_GUIDE.md`
