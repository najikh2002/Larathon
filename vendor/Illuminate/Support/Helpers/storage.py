"""
Storage Helper Functions
Convenient functions for file storage operations
"""
from vendor.Illuminate.Filesystem.Storage import Storage


def storage_path(path: str = "") -> str:
    """Get path to storage directory"""
    import os
    base = os.path.join(os.getcwd(), "storage", "app")
    if path:
        return os.path.join(base, path.lstrip('/'))
    return base


def public_path(path: str = "") -> str:
    """Get path to public directory"""
    import os
    base = os.path.join(os.getcwd(), "public")
    if path:
        return os.path.join(base, path.lstrip('/'))
    return base


def asset(path: str) -> str:
    """Generate URL for asset"""
    return f"/static/{path.lstrip('/')}"


def storage_url(path: str, disk: str = None) -> str:
    """Generate public URL for stored file"""
    return Storage.url(path, disk)


def upload_file(file, directory: str = "", disk: str = None, name: str = None) -> str:
    """
    Upload file and return path
    
    Args:
        file: File object (from request.files) - UploadFile from Starlette
        directory: Directory to store in
        disk: Storage disk to use
        name: Custom filename (optional)
    
    Returns:
        Stored file path
    """
    import os
    from datetime import datetime
    import asyncio
    
    # Check if file has filename
    if not hasattr(file, 'filename') or not file.filename:
        raise ValueError("Invalid file object - no filename")
    
    # Generate filename
    if name:
        filename = name
    else:
        # Use original filename
        filename = file.filename
        
        # Add timestamp to avoid collisions
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{name}_{timestamp}{ext}"
    
    # Build path
    if directory:
        path = f"{directory.rstrip('/')}/{filename}"
    else:
        path = filename
    
    # Read file content
    # For UploadFile (Starlette), we need to read the content
    if hasattr(file, 'read'):
        # Check if it's async
        if asyncio.iscoroutinefunction(file.read):
            # This is async - need to handle it differently
            # For now, we'll use file.file which is sync
            if hasattr(file, 'file'):
                file_content = file.file.read()
            else:
                raise ValueError("Cannot read file content - async context required")
        else:
            file_content = file.read()
    else:
        raise ValueError("File object does not have read() method")
    
    # Store file
    Storage.put(path, file_content, disk)
    
    return path


def delete_file(path: str, disk: str = None) -> bool:
    """Delete a stored file"""
    return Storage.delete(path, disk)


def file_exists(path: str, disk: str = None) -> bool:
    """Check if file exists in storage"""
    return Storage.exists(path, disk)


def get_file_url(path: str, disk: str = None) -> str:
    """Get public URL for file"""
    return Storage.url(path, disk)
