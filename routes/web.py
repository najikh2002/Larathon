"""
Web Routes - Using Improved Router
Laravel-style routing with middleware, groups, and named routes
"""
from vendor.Illuminate.Routing.ImprovedRouter import Route
from app.Http.Controllers.WelcomeController import WelcomeController
from app.Http.Controllers.TestController import TestController
from app.Http.Controllers.TodoController import TodoController
from app.Http.Controllers.AuthController import AuthController
from app.Http.Controllers.DashboardController import DashboardController
from app.Http.Controllers.PostController import PostController
from app.Http.Controllers.StorageController import StorageController


def register_routes():
    """Register all application routes"""

    # =====================================
    # Public Routes
    # =====================================
    Route.get('/', WelcomeController, 'index').name('home')
    Route.get('/test', TestController, 'index').name('test')
    Route.get('/coba', TestController, 'coba').name('coba')

    # =====================================
    # Authentication Routes
    # =====================================
    Route.get('/login', AuthController, 'show_login').name('login')
    Route.post('/login', AuthController, 'login')
    Route.get('/register', AuthController, 'show_register').name('register')
    Route.post('/register', AuthController, 'register')
    Route.get('/logout', AuthController, 'logout').name('logout')

    # =====================================
    # Protected Routes (Require Auth)
    # =====================================
    Route.middleware(['auth']).group(lambda: [
        # Dashboard
        Route.get('/dashboard', DashboardController, 'index').name('dashboard'),

        # Profile
        Route.get('/profile', AuthController, 'profile').name('profile'),

        # Posts Management
        Route.prefix('posts').name('posts.').group(lambda: [
            Route.get('/', PostController, 'index').name('index'),
            Route.get('/create', PostController, 'create').name('create'),
            Route.post('/', PostController, 'store').name('store'),
            Route.get('/{post_id}/edit', PostController, 'edit').name('edit'),
            Route.post('/{post_id}', PostController, 'update').name('update'),
            Route.post('/{post_id}/delete', PostController, 'destroy').name('destroy'),
        ]),

        # Storage Management
        Route.prefix('storage').name('storage.').group(lambda: [
            Route.get('/', StorageController, 'index').name('index'),
            Route.post('/upload', StorageController, 'upload').name('upload'),
            Route.delete('/delete/{path}', StorageController, 'delete').name('delete'),
        ]),
    ])

    # Todos (Resource)
    Route.resource('todos', TodoController),

    # =====================================
    # Admin Routes (Auth + Admin)
    # =====================================
    # Route.prefix('admin').middleware(['auth', 'admin']).name('admin.').group(lambda: [
    #     # Add admin routes here when needed
    # ])


def route(name: str, params: dict = None) -> str:
    """
    Generate URL from named route

    Usage:
        url = route('posts.show', {'post_id': 1})  # /posts/1
        url = route('dashboard')  # /dashboard
    """
    return Route.get_named_route(name, params)
