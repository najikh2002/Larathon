#!/usr/bin/env python
"""
Simple test to check if the issue is with routing or form parsing
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/test-direct")
async def test_direct(file: UploadFile = File(...)):
    """Direct FastAPI file upload - should work"""
    content = await file.read()
    return {
        "success": True,
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type
    }

@app.post("/test-form")
async def test_form_manual(request):
    """Manual form parsing like our controller"""
    from starlette.requests import Request
    form = await request.form()
    
    return {
        "form_keys": list(form.keys()),
        "has_file": "file" in form,
        "form_items": list(form.items())[:5]  # First 5 items
    }

if __name__ == "__main__":
    print("Starting test server on http://127.0.0.1:8001")
    print("Test endpoints:")
    print("  POST http://127.0.0.1:8001/test-direct (FastAPI native)")
    print("  POST http://127.0.0.1:8001/test-form (Manual parsing)")
    uvicorn.run(app, host="127.0.0.1", port=8001)
