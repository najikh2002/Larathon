"""
Authentication Middleware
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from vendor.Illuminate.Auth.JWT import JWT
from app.Models.User import User


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware
    Protects routes that require authentication
    """
    
    async def dispatch(self, request, call_next):
        # Get token from cookie or header
        token = request.cookies.get('auth_token')
        
        if not token:
            # Try Authorization header
            auth_header = request.headers.get('Authorization')
            token = JWT.extract_from_header(auth_header)
        
        # Decode token
        payload = JWT.decode(token) if token else None
        
        # Attach user info to request state
        if payload:
            request.state.user = payload
            request.state.authenticated = True
        else:
            request.state.user = None
            request.state.authenticated = False
        
        response = await call_next(request)
        return response


def require_auth(func):
    """
    Decorator to require authentication for a route
    Usage: @require_auth
    """
    async def wrapper(self, request, *args, **kwargs):
        if not getattr(request.state, 'authenticated', False):
            # Check if it's an API request
            if request.url.path.startswith('/api/'):
                return JSONResponse(
                    {'error': 'Unauthorized', 'message': 'Authentication required'},
                    status_code=401
                )
            # Redirect to login for web requests
            return RedirectResponse(url=f'/login?redirect={request.url.path}', status_code=302)
        
        return await func(self, request, *args, **kwargs)
    
    return wrapper


def require_role(role: str):
    """
    Decorator to require specific role
    Usage: @require_role('admin')
    """
    def decorator(func):
        async def wrapper(self, request, *args, **kwargs):
            if not getattr(request.state, 'authenticated', False):
                if request.url.path.startswith('/api/'):
                    return JSONResponse(
                        {'error': 'Unauthorized', 'message': 'Authentication required'},
                        status_code=401
                    )
                return RedirectResponse(url=f'/login?redirect={request.url.path}', status_code=302)
            
            user_role = request.state.user.get('role', 'user')
            if user_role != role:
                if request.url.path.startswith('/api/'):
                    return JSONResponse(
                        {'error': 'Forbidden', 'message': f'Requires {role} role'},
                        status_code=403
                    )
                return JSONResponse(
                    {'error': 'Access denied', 'message': f'Requires {role} role'},
                    status_code=403
                )
            
            return await func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


async def get_current_user(request):
    """Helper function to get current authenticated user"""
    if not getattr(request.state, 'authenticated', False):
        return None
    
    user_id = request.state.user.get('user_id')
    if not user_id:
        return None
    
    return await User.find(user_id)
