"""
Improved Router with Laravel-style features
- Middleware support
- Route groups
- Named routes
- Prefix support
"""
from fastapi import APIRouter, Request, Form
from typing import Callable, List, Dict, Optional
from vendor.Illuminate.Routing.RouteGroup import RouteGroup, PendingRoute
import inspect
from inspect import signature


class ImprovedRoute:
    """
    Improved Route class with Laravel-style features
    
    Usage:
        # Basic routes
        Route.get('/posts', PostController, 'index')
        
        # With middleware
        Route.get('/dashboard', DashboardController, 'index').middleware(['auth'])
        
        # Named routes
        Route.get('/posts/{id}', PostController, 'show').name('posts.show')
        
        # Route groups
        Route.prefix('admin').middleware(['auth', 'admin']).group(lambda:
            Route.get('/users', UserController, 'index').name('users.index')
            Route.get('/posts', PostController, 'index').name('posts.index')
        )
        
        # Nested groups
        Route.prefix('api').group(lambda:
            Route.prefix('v1').group(lambda:
                Route.get('/users', ApiUserController, 'index')
            )
        )
    """
    
    router = APIRouter()
    _current_group = None
    _named_routes = {}
    _middleware_stack = {}
    
    @classmethod
    def get(cls, path: str, controller, action: str):
        """Register GET route"""
        pending = PendingRoute('GET', path, controller, action, cls)
        pending.register()
        return pending
    
    @classmethod
    def post(cls, path: str, controller, action: str):
        """Register POST route"""
        pending = PendingRoute('POST', path, controller, action, cls)
        pending.register()
        return pending
    
    @classmethod
    def put(cls, path: str, controller, action: str):
        """Register PUT route"""
        pending = PendingRoute('PUT', path, controller, action, cls)
        pending.register()
        return pending
    
    @classmethod
    def delete(cls, path: str, controller, action: str):
        """Register DELETE route"""
        pending = PendingRoute('DELETE', path, controller, action, cls)
        pending.register()
        return pending
    
    @classmethod
    def patch(cls, path: str, controller, action: str):
        """Register PATCH route"""
        pending = PendingRoute('PATCH', path, controller, action, cls)
        pending.register()
        return pending
    
    @classmethod
    def prefix(cls, prefix: str):
        """Start a new route group with prefix"""
        group = RouteGroup()
        return group.prefix(prefix)
    
    @classmethod
    def middleware(cls, middleware: List[str]):
        """Start a new route group with middleware"""
        group = RouteGroup()
        return group.middleware(middleware)
    
    @classmethod
    def name(cls, name: str):
        """Start a new route group with name prefix"""
        group = RouteGroup()
        return group.name(name)
    
    @classmethod
    def group(cls, attributes: Dict, callback: Callable):
        """Create route group with attributes dict"""
        group = RouteGroup()
        
        if 'prefix' in attributes:
            group.prefix(attributes['prefix'])
        if 'middleware' in attributes:
            group.middleware(attributes['middleware'])
        if 'name' in attributes:
            group.name(attributes['name'])
        if 'namespace' in attributes:
            group.namespace(attributes['namespace'])
        
        return group.group(callback)
    
    @classmethod
    def resource(cls, name: str, controller):
        """Register resource routes (CRUD)"""
        group = cls._current_group or {}
        prefix = group.get('prefix', '')
        name_prefix = group.get('name', '')
        middleware = group.get('middleware', [])
        
        # Build full path
        base_path = f"/{prefix}/{name}".replace('//', '/').rstrip('/')
        
        # Register all resource routes
        routes = [
            ('GET', f"{base_path}", 'index', f"{name_prefix}{name}.index"),
            ('GET', f"{base_path}/create", 'create', f"{name_prefix}{name}.create"),
            ('POST', f"{base_path}", 'store', f"{name_prefix}{name}.store"),
            ('GET', f"{base_path}/{{id}}", 'show', f"{name_prefix}{name}.show"),
            ('GET', f"{base_path}/{{id}}/edit", 'edit', f"{name_prefix}{name}.edit"),
            ('PUT', f"{base_path}/{{id}}", 'update', f"{name_prefix}{name}.update"),
            ('DELETE', f"{base_path}/{{id}}", 'destroy', f"{name_prefix}{name}.destroy"),
        ]
        
        for method, path, action, route_name in routes:
            cls._register_route(method, path, controller, action, middleware, route_name)
    
    @classmethod
    def _register_route(cls, method: str, path: str, controller, action: str, 
                       middleware: List[str] = None, name: str = None):
        """Internal method to register route with FastAPI"""
        # Store middleware for this route
        if middleware:
            cls._middleware_stack[path] = middleware
        
        # Store named route
        if name:
            cls._named_routes[name] = path
        
        # Get controller instance and method
        controller_instance = controller() if callable(controller) else controller
        handler = getattr(controller_instance, action)
        
        # Inspect handler signature to check if it needs form data injection
        handler_sig = signature(handler)
        needs_form_injection = any(
            param.annotation == Form or 
            (hasattr(param.annotation, '__origin__') and param.annotation.__origin__ == type(Form))
            for param in handler_sig.parameters.values()
            if param.name != 'request' and param.name != 'self'
        )
        
        # Create wrapper function with proper signature
        if middleware:
            # With middleware - wrap the handler
            async def route_handler(request: Request):
                """Wrapper that executes middleware before controller"""
                
                # DEBUG: Check request details
                print(f"DEBUG Router: Method={request.method}, Path={request.url.path}")
                print(f"DEBUG Router: Content-Type={request.headers.get('content-type')}")
                
                # Execute middleware chain
                for middleware_name in middleware:
                    # Check auth middleware
                    if middleware_name == 'auth':
                        if not getattr(request.state, 'authenticated', False):
                            from starlette.responses import RedirectResponse, JSONResponse
                            if request.url.path.startswith('/api/'):
                                return JSONResponse(
                                    {'error': 'Unauthorized', 'message': 'Authentication required'},
                                    status_code=401
                                )
                            return RedirectResponse(url=f'/login?redirect={request.url.path}', status_code=302)
                    
                    # Check admin middleware
                    elif middleware_name == 'admin':
                        user_role = request.state.user.get('role', 'user') if hasattr(request.state, 'user') else 'user'
                        if user_role != 'admin':
                            from starlette.responses import JSONResponse
                            return JSONResponse(
                                {'error': 'Forbidden', 'message': 'Requires admin role'},
                                status_code=403
                            )
                
                # Get path parameters from request
                path_params = request.path_params
                
                # Call the actual controller method
                if inspect.iscoroutinefunction(handler):
                    return await handler(request, **path_params)
                else:
                    return handler(request, **path_params)
        else:
            # Without middleware - use handler directly
            async def route_handler(request: Request):
                """Direct handler without middleware"""
                # DEBUG
                print(f"DEBUG Router (no middleware): Method={request.method}, Path={request.url.path}")
                print(f"DEBUG Router: Content-Type={request.headers.get('content-type')}")
                
                path_params = request.path_params
                
                if inspect.iscoroutinefunction(handler):
                    return await handler(request, **path_params)
                else:
                    return handler(request, **path_params)
        
        # Register with FastAPI router based on method
        methods_map = {
            'GET': cls.router.get,
            'POST': cls.router.post,
            'PUT': cls.router.put,
            'DELETE': cls.router.delete,
            'PATCH': cls.router.patch,
        }
        
        route_decorator = methods_map.get(method.upper())
        if route_decorator:
            route_decorator(path)(route_handler)
    
    @classmethod
    def get_named_route(cls, name: str, params: Dict = None) -> str:
        """Get URL for named route"""
        if name not in cls._named_routes:
            raise ValueError(f"Route '{name}' not found")
        
        path = cls._named_routes[name]
        
        # Replace parameters
        if params:
            for key, value in params.items():
                path = path.replace(f"{{{key}}}", str(value))
        
        return path
    
    @classmethod
    def has_middleware(cls, path: str, middleware_name: str) -> bool:
        """Check if route has specific middleware"""
        route_middleware = cls._middleware_stack.get(path, [])
        return middleware_name in route_middleware


# Create global instance
Route = ImprovedRoute
