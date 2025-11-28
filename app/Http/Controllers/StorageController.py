from app.Http.Controllers.Controller import Controller
from vendor.Illuminate.Filesystem.Storage import Storage
from vendor.Illuminate.Support.Helpers.storage import upload_file, get_file_url
from fastapi import UploadFile, File, Form
from typing import Optional


class StorageController(Controller):
    """
    Storage Controller
    Example controller showing file upload/download with external storage
    """
    
    def index(self, request):
        """Show upload form and list uploaded files"""
        # Get list of files from storage
        try:
            files = Storage.files("uploads")
            
            # Get URLs for each file
            file_list = []
            for file_path in files:
                file_list.append({
                    'path': file_path,
                    'url': Storage.url(file_path),
                    'name': file_path.split('/')[-1]
                })
        except Exception as e:
            print(f"Error listing files: {e}")
            file_list = []
        
        return self.view("storage.index", request, {"files": file_list})
    
    async def upload(self, request):
        """Handle file upload - SIMPLIFIED VERSION"""
        try:
            print("=== Upload Request ===")
            
            # Try FastAPI way first (if available)
            if hasattr(request, 'form'):
                form = await request.form()
                print(f"Form parsed, keys: {list(form.keys())}")
            else:
                # Fallback to direct Starlette request
                from starlette.requests import Request
                if isinstance(request, Request):
                    form = await request.form()
                    print(f"Starlette form parsed, keys: {list(form.keys())}")
                else:
                    return {"error": "Cannot parse request"}
            
            if not form or "file" not in form:
                return {"error": "No file in form", "form_keys": list(form.keys()) if form else []}
            
            file = form["file"]
            print(f"✅ File received!")
            print(f"Filename: {file.filename}")
            print(f"Content-Type: {file.content_type}")
            
            # Read file content
            file_content = await file.read()
            
            print(f"File size: {len(file_content)} bytes")
            
            # Generate path
            import os
            from datetime import datetime
            name, ext = os.path.splitext(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            path = f"uploads/{filename}"
            
            # Store using Storage facade
            Storage.put(path, file_content)
            
            print(f"File uploaded to: {path}")
            
            # Get public URL
            file_url = Storage.url(path)
            
            print(f"File URL: {file_url}")
            
            return self.redirect("/storage")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Upload error: {error_trace}")
            return {"error": str(e), "traceback": error_trace}
    
    async def upload_fallback(self, request):
        """Fallback method using manual form parsing"""
        try:
            print("Using fallback manual form parsing...")
            
            # Debug: Check request details
            print(f"Request method: {request.method}")
            print(f"Request URL: {request.url}")
            print(f"Content-Type: {request.headers.get('content-type', 'N/A')}")
            
            # Check if request body is already consumed
            if hasattr(request, '_stream_consumed'):
                print(f"Stream consumed: {request._stream_consumed}")
            
            # Get uploaded file
            form = await request.form()
            
            # Debug logging
            print(f"Form keys: {list(form.keys())}")
            print(f"Form items count: {len(list(form.items()))}")
            
            if "file" not in form:
                return {
                    "error": "No file provided", 
                    "form_keys": list(form.keys()),
                    "content_type": request.headers.get('content-type', 'N/A'),
                    "method": request.method
                }
            
            file = form["file"]
            
            print(f"File object: {file}")
            print(f"Uploading file: {file.filename}")
            
            # Read file content
            file_content = await file.read()
            
            print(f"File size: {len(file_content)} bytes")
            
            # Generate path
            import os
            from datetime import datetime
            name, ext = os.path.splitext(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            path = f"uploads/{filename}"
            
            # Store using Storage facade
            Storage.put(path, file_content)
            
            print(f"File uploaded to: {path}")
            
            return self.redirect("/storage")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Upload error: {error_trace}")
            return {"error": str(e), "traceback": error_trace}
    
    def show(self, request, path):
        """Serve a file (for local storage only)"""
        try:
            # Only works with local driver
            file_content = Storage.get(path)
            
            from fastapi.responses import Response
            
            # Detect content type
            if path.endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.gif'):
                content_type = 'image/gif'
            else:
                content_type = 'application/octet-stream'
            
            return Response(content=file_content, media_type=content_type)
            
        except Exception as e:
            return {"error": "File not found"}
    
    def delete(self, request, path):
        """Delete a file"""
        try:
            Storage.delete(path)
            return self.redirect("/storage")
        except Exception as e:
            return {"error": str(e)}
