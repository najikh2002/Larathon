# Improved Routing System - Complete Documentation

## Overview
Laravel-style routing system with middleware, route groups, prefixes, named routes, and nested groups.

## Features

### 1. Middleware Support
Apply middleware to routes or groups:

```python
# Single route with middleware
Route.get('/dashboard', DashboardController, 'index')\
     .middleware(['auth'])\
     .name('dashboard')

# Group with middleware
Route.middleware(['auth']).group(lambda: [
    Route.get('/dashboard', DashboardController, 'index'),
    Route.get('/profile', ProfileController, 'index'),
])
```

**Built-in Middleware:**
- `auth` - Requires authentication, redirects to /login
- `admin` - Requires admin role, returns 403 if not admin

### 2. Route Prefixes
Group routes under a common prefix:

```python
# All routes will be under /admin/*
Route.prefix('admin').group(lambda: [
    Route.get('/users', UserController, 'index'),      # /admin/users
    Route.get('/posts', PostController, 'index'),      # /admin/posts
])
```

### 3. Named Routes
Name routes for easy URL generation:

```python
# Define named route
Route.get('/posts/{id}', PostController, 'show').name('posts.show')

# Generate URL
url = route('posts.show', {'id': 1})  # Returns: /posts/1
```

### 4. Name Prefixes
Apply name prefix to all routes in group:

```python
Route.name('posts.').group(lambda: [
    Route.get('/', PostController, 'index').name('index'),    # posts.index
    Route.get('/{id}', PostController, 'show').name('show'),  # posts.show
])
```

### 5. Nested Groups
Groups within groups with attribute merging:

```python
Route.prefix('api').name('api.').group(lambda: [
    Route.prefix('v1').name('v1.').group(lambda: [
        Route.get('/users', ApiController, 'users').name('users'),  
        # URL: /api/v1/users
        # Name: api.v1.users
    ])
])
```

### 6. Combined Attributes
Mix multiple attributes in one group:

```python
Route.prefix('admin')\
     .middleware(['auth', 'admin'])\
     .name('admin.')\
     .group(lambda: [
    Route.get('/dashboard', AdminController, 'index').name('index'),
    # URL: /admin/dashboard
    # Name: admin.index
    # Middleware: ['auth', 'admin']
])
```

### 7. Resource Routes
Generate standard CRUD routes:

```python
Route.resource('posts', PostController)
# Generates:
# GET    /posts              -> index
# GET    /posts/create       -> create
# POST   /posts              -> store
# GET    /posts/{id}         -> show
# GET    /posts/{id}/edit    -> edit
# PUT    /posts/{id}         -> update
# DELETE /posts/{id}         -> destroy
```

## Complete Example

```python
from vendor.Illuminate.Routing.ImprovedRouter import Route

def register_routes():
    # Public routes
    Route.get('/', WelcomeController, 'index').name('home')
    
    # Auth routes
    Route.prefix('').name('auth.').group(lambda: [
        Route.get('/login', AuthController, 'show_login').name('login'),
        Route.post('/login', AuthController, 'login'),
    ])
    
    # Protected routes
    Route.middleware(['auth']).group(lambda: [
        Route.get('/dashboard', DashboardController, 'index').name('dashboard'),
        
        # Posts with prefix
        Route.prefix('posts').name('posts.').group(lambda: [
            Route.get('/', PostController, 'index').name('index'),
            Route.get('/{id}', PostController, 'show').name('show'),
        ])
    ])
    
    # Admin area
    Route.prefix('admin')\
         .middleware(['auth', 'admin'])\
         .name('admin.')\
         .group(lambda: [
        Route.resource('users', AdminUserController),
    ])

# Helper function
def route(name: str, params: dict = None) -> str:
    """Generate URL from named route"""
    return Route.get_named_route(name, params)
```

## Migration from Basic Router

### Before (Basic):
```python
from vendor.Illuminate.Routing.Router import Route

Route.get('/admin/users', UserController, 'index')
Route.get('/admin/posts', PostController, 'index')
Route.get('/admin/settings', SettingsController, 'index')
# Repetitive, no middleware, no named routes
```

### After (Improved):
```python
from vendor.Illuminate.Routing.ImprovedRouter import Route

Route.prefix('admin').middleware(['auth', 'admin']).name('admin.').group(lambda: [
    Route.get('/users', UserController, 'index').name('index'),
    Route.get('/posts', PostController, 'index').name('index'),
    Route.get('/settings', SettingsController, 'index').name('index'),
])
# Clean, DRY, middleware applied, named routes!
```

## Files Structure

```
vendor/Illuminate/Routing/
├── Router.py               # Original router (kept for compatibility)
├── ImprovedRouter.py       # New router with all features
└── RouteGroup.py          # Group management

routes/
├── web.py                 # Your route definitions
└── web_improved_example.py # Complete examples
```

## Architecture

### ImprovedRouter
Main router class that handles:
- Route registration
- Middleware wrapping
- Named route storage
- URL generation

### RouteGroup
Handles group attributes:
- Prefix merging
- Name concatenation
- Middleware stacking
- Nested group support

### PendingRoute
Chainable route definition:
- Allows `.middleware(['auth'])`
- Allows `.name('posts.show')`
- Registers route with all attributes

## Middleware System

### Auth Middleware
- Checks `request.state.authenticated`
- Web routes: Redirects to `/login?redirect={path}`
- API routes: Returns 401 JSON

### Admin Middleware
- Checks `request.state.user.role == 'admin'`
- Returns 403 JSON if not admin

### Custom Middleware
Add your own by extending the middleware checking in `ImprovedRouter._register_route()`:

```python
elif middleware_name == 'custom':
    # Your custom middleware logic
    if not some_condition:
        return JSONResponse({'error': 'Forbidden'}, status_code=403)
```

## URL Generation

### Basic
```python
url = route('posts.show', {'id': 1})
# Returns: /posts/1
```

### With Multiple Parameters
```python
url = route('posts.comments.show', {'post_id': 1, 'id': 5})
# Returns: /posts/1/comments/5
```

### Without Parameters
```python
url = route('dashboard')
# Returns: /dashboard
```

## Benefits

1. **DRY** - No repetition of prefixes or middleware
2. **Organized** - Clear route structure
3. **Type-safe** - IDE autocomplete support
4. **Laravel-like** - Familiar for Laravel developers
5. **Maintainable** - Easy to update and refactor
6. **Scalable** - Works with any size codebase
7. **Flexible** - Mix and match features as needed

## Common Patterns

### API Routes
```python
Route.prefix('api').name('api.').group(lambda: [
    Route.prefix('v1').name('v1.').group(lambda: [
        # Public API
        Route.get('/status', ApiController, 'status').name('status'),
        
        # Authenticated API
        Route.middleware(['auth']).group(lambda: [
            Route.get('/user', ApiController, 'user').name('user'),
        ])
    ])
])
```

### Admin Dashboard
```python
Route.prefix('admin').middleware(['auth', 'admin']).name('admin.').group(lambda: [
    Route.get('/dashboard', AdminController, 'index').name('dashboard'),
    Route.resource('users', AdminUserController),
    Route.resource('posts', AdminPostController),
])
```

### Protected Content Management
```python
Route.middleware(['auth']).group(lambda: [
    Route.prefix('posts').name('posts.').group(lambda: [
        Route.get('/', PostController, 'index').name('index'),
        Route.get('/create', PostController, 'create').name('create'),
        Route.post('/', PostController, 'store').name('store'),
    ])
])
```

## Testing Routes

Start server:
```bash
python artisan.py serve
```

Test public routes:
- http://localhost:8000/
- http://localhost:8000/login

Test protected routes (should redirect):
- http://localhost:8000/dashboard
- http://localhost:8000/posts

Register and test:
1. http://localhost:8000/register
2. Create account
3. Access protected routes

## Summary

This improved routing system brings Larathon closer to Laravel's elegant routing while maintaining FastAPI's performance and async capabilities. It's production-ready and fully compatible with the existing auth and storage systems.
