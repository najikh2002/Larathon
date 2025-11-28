"""
Welcome Controller
"""
from app.Http.Controllers.Controller import Controller
from app.Http.Middleware.AuthMiddleware import get_current_user


class WelcomeController(Controller):
    """Handle welcome page"""
    
    async def index(self, request):
        """Show welcome page"""
        # Get current user if authenticated
        user = await get_current_user(request) if getattr(request.state, 'authenticated', False) else None
        
        return self.view('welcome', request, {'user': user})
