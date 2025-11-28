"""
Test if body can be read in wrapper
"""
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
import uvicorn

async def test_endpoint(request):
    """Test endpoint"""
    print(f"1. In handler, method: {request.method}")
    print(f"2. Content-Type: {request.headers.get('content-type')}")
    
    # Try to read body
    try:
        body = await request.body()
        print(f"3. Body bytes: {body}")
        
        # Try to read form (after body)
        form = await request.form()
        print(f"4. Form data: {dict(form)}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    return PlainTextResponse("Test complete - check console")

app = Starlette(debug=True, routes=[
    Route('/test', test_endpoint, methods=['POST']),
])

if __name__ == "__main__":
    print("Test server on http://localhost:8002/test")
    print("Send: curl -X POST http://localhost:8002/test -d 'email=test@test.com&password=pass123'")
    uvicorn.run(app, host="127.0.0.1", port=8002)
