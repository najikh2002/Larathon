"""
Route Group - Laravel-style route grouping
"""
from typing import List, Dict, Callable, Optional


class RouteGroup:
    """
    Route group for applying common attributes to multiple routes
    
    Usage:
        Route.prefix('admin').middleware(['auth']).group(lambda:
            Route.get('/users', UserController, 'index')
            Route.get('/posts', PostController, 'index')
        )
    """
    
    def __init__(self):
        self.attributes = {
            'prefix': '',
            'name': '',
            'middleware': [],
            'namespace': ''
        }
    
    def prefix(self, prefix: str):
        """Set URL prefix for all routes in group"""
        self.attributes['prefix'] = prefix.strip('/')
        return self
    
    def name(self, name: str):
        """Set name prefix for all routes in group"""
        self.attributes['name'] = name
        return self
    
    def middleware(self, middleware: List[str]):
        """Set middleware for all routes in group"""
        if isinstance(middleware, str):
            middleware = [middleware]
        self.attributes['middleware'] = middleware
        return self
    
    def namespace(self, namespace: str):
        """Set controller namespace for all routes in group"""
        self.attributes['namespace'] = namespace
        return self
    
    def group(self, callback: Callable):
        """Execute the group callback with current attributes"""
        # Store current group context
        from vendor.Illuminate.Routing.ImprovedRouter import ImprovedRoute
        previous_group = ImprovedRoute._current_group
        
        # Merge with parent group if exists
        if previous_group:
            merged_attributes = {
                'prefix': f"{previous_group['prefix']}/{self.attributes['prefix']}".strip('/'),
                'name': f"{previous_group['name']}{self.attributes['name']}",
                'middleware': previous_group['middleware'] + self.attributes['middleware'],
                'namespace': self.attributes['namespace'] or previous_group['namespace']
            }
            ImprovedRoute._current_group = merged_attributes
        else:
            ImprovedRoute._current_group = self.attributes.copy()
        
        # Execute callback to register routes
        callback()
        
        # Restore previous group context
        ImprovedRoute._current_group = previous_group
        
        return self


class PendingRoute:
    """
    Pending route that can have middleware and name applied
    
    Usage:
        Route.get('/dashboard', DashboardController, 'index')
             .middleware(['auth'])
             .name('dashboard')
    """
    
    def __init__(self, method: str, path: str, controller, action: str, router):
        self.method = method
        self.path = path
        self.controller = controller
        self.action = action
        self.router = router
        self.route_middleware = []
        self.route_name = None
    
    def middleware(self, middleware: List[str]):
        """Add middleware to this specific route"""
        if isinstance(middleware, str):
            middleware = [middleware]
        self.route_middleware = middleware
        return self
    
    def name(self, name: str):
        """Set name for this route"""
        self.route_name = name
        return self
    
    def register(self):
        """Register the route with all attributes"""
        # Get current group attributes
        from vendor.Illuminate.Routing.ImprovedRouter import ImprovedRoute
        group = ImprovedRoute._current_group or {}
        
        # Merge path with group prefix
        prefix = group.get('prefix', '').strip('/')
        path = self.path.strip('/')
        
        if prefix and path:
            full_path = f"/{prefix}/{path}"
        elif prefix:
            full_path = f"/{prefix}"
        elif path:
            full_path = f"/{path}"
        else:
            full_path = '/'
        
        # Merge middleware
        all_middleware = group.get('middleware', []) + self.route_middleware
        
        # Merge name
        full_name = f"{group.get('name', '')}{self.route_name or ''}"
        
        # Register the route with router
        self.router._register_route(
            self.method,
            full_path,
            self.controller,
            self.action,
            middleware=all_middleware,
            name=full_name
        )
