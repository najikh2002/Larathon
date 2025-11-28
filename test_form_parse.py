"""
Test if FastAPI can parse form data
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/test-form")
async def show_form():
    return HTMLResponse("""
    <html>
    <body>
        <h1>Test Form</h1>
        <form method="POST" action="/test-login">
            <input type="email" name="email" value="test@example.com">
            <input type="password" name="password" value="password123">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """)

@app.post("/test-login")
async def test_login(request: Request):
    form = await request.form()
    print(f"Form data: {dict(form)}")
    email = form.get('email')
    password = form.get('password')
    print(f"Email: {email}, Password: {password}")
    return {"email": email, "password": password}

if __name__ == "__main__":
    print("Test server starting on http://localhost:8001/test-form")
    uvicorn.run(app, host="127.0.0.1", port=8001)
