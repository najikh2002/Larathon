"""
Test login form submission
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.Http.Controllers.AuthController import AuthController
from starlette.datastructures import FormData
from unittest.mock import Mock

async def test_login():
    print("Testing login logic...")
    
    # Create mock request
    request = Mock()
    
    # Simulate form data
    form_data = FormData({
        'email': 'admin@larathon.app',
        'password': 'admin123',
        'redirect_to': '/dashboard'
    })
    
    async def mock_form():
        return form_data
    
    request.form = mock_form
    
    # Test controller
    controller = AuthController()
    
    try:
        result = await controller.login(request)
        print(f"✅ Login result: {type(result)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login())
