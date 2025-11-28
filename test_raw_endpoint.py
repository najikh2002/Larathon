"""
Test raw FastAPI - bypass everything
"""
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def show_form():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Test Raw</title></head>
    <body>
        <h1>Test Raw FastAPI</h1>
        <form method="POST" action="/test-post" enctype="application/x-www-form-urlencoded">
            <input type="email" name="email" value="admin@larathon.app"><br>
            <input type="password" name="password" value="admin123"><br>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """)

@app.post("/test-post")
async def test_post(request: Request):
    print("="*60)
    print("RAW FASTAPI TEST")
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.headers.get('content-type')}")
    print(f"Content-Length: {request.headers.get('content-length')}")
    
    # Read body
    body = await request.body()
    print(f"Body length: {len(body)}")
    print(f"Body: {body.decode('utf-8') if body else 'EMPTY'}")
    print("="*60)
    
    return PlainTextResponse(f"Body length: {len(body)}\nBody: {body.decode('utf-8') if body else 'EMPTY'}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAW FASTAPI TEST SERVER")
    print("="*60)
    print("\nOpen: http://localhost:8003")
    print("\nThis will test if FastAPI can receive form data")
    print("without any of our custom routing/middleware.")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="info")
