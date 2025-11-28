# Authentication System Guide - Larathon

## Overview

Larathon now includes a complete, production-ready authentication system with:
- ✅ User registration & login
- ✅ JWT-based authentication
- ✅ Role-based access control (user, admin)
- ✅ Protected routes with middleware
- ✅ Password hashing (bcrypt)
- ✅ Session management via cookies
- ✅ Content management with image uploads
- ✅ Dashboard & CRUD interface

## Quick Start

### 1. Run Migrations

```bash
python artisan.py migrate
```

This creates the `users` and `posts` tables.

### 2. Start Server

```bash
python artisan.py serve
```

### 3. Register an Account

Visit `http://localhost:8000/register` and create your first account.

### 4. Start Creating Content

Go to `http://localhost:8000/dashboard` and click "Create New Post".

## Architecture

### Authentication Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ POST /register
       ▼
┌──────────────────┐
│ AuthController   │
│ - Validate data  │
│ - Hash password  │
│ - Create user    │
│ - Generate JWT   │
└──────┬───────────┘
       │ Set auth_token cookie
       ▼
┌──────────────────┐
│ AuthMiddleware   │
│ - Extract token  │
│ - Decode JWT     │
│ - Set user state │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Protected Routes │
│ - Dashboard      │
│ - Posts CRUD     │
└──────────────────┘
```

### Components

#### 1. Models

**User Model** (`app/Models/User.py`):
- Handles user data
- Password hashing & verification
- Role management (user, admin)
- Relationship with posts

**Post Model** (`app/Models/Post.py`):
- Content management
- Slug auto-generation
- Status (draft/published)
- Image upload integration

#### 2. JWT Authentication

**JWT Helper** (`vendor/Illuminate/Auth/JWT.py`):
```python
from vendor.Illuminate.Auth.JWT import JWT

# Generate token
token = JWT.generate(user_id, email, role)

# Decode token
payload = JWT.decode(token)
# Returns: {'user_id': 1, 'email': 'user@example.com', 'role': 'user'}

# Verify token
is_valid = JWT.verify(token)
```

**Token Structure**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "iat": 1234567890
}
```

#### 3. Middleware

**AuthMiddleware** (`app/Http/Middleware/AuthMiddleware.py`):
- Automatically runs on every request
- Extracts JWT from cookie or Authorization header
- Decodes and validates token
- Attaches user info to `request.state`

**Usage in Controllers**:
```python
from app.Http.Middleware.AuthMiddleware import require_auth, get_current_user

class MyController(Controller):
    @require_auth
    async def protected_route(self, request):
        user = await get_current_user(request)
        return {"user": user.name}
```

#### 4. Controllers

**AuthController**:
- `show_login()` - Login form
- `login()` - Login handler
- `show_register()` - Register form
- `register()` - Register handler
- `logout()` - Logout handler
- `profile()` - User profile

**DashboardController**:
- `index()` - Dashboard with stats

**PostController**:
- `index()` - List posts
- `create()` - Create form
- `store()` - Save post
- `edit()` - Edit form
- `update()` - Update post
- `destroy()` - Delete post

## Features

### 1. User Registration

**Endpoint**: `POST /register`

**Form Fields**:
- Name (required, min 2 chars)
- Email (required, unique)
- Password (required, min 6 chars)
- Password Confirmation (required, must match)

**Validation**:
- Name length check
- Email format & uniqueness
- Password strength & match
- Returns errors to form if invalid

**On Success**:
- User created with hashed password
- JWT token generated
- Cookie set with token
- Redirect to dashboard

### 2. User Login

**Endpoint**: `POST /login`

**Form Fields**:
- Email (required)
- Password (required)

**Validation**:
- Email exists
- Password matches
- Account is active

**On Success**:
- JWT token generated
- Cookie set with token
- Redirect to dashboard or specified page

### 3. Protected Routes

Use the `@require_auth` decorator:

```python
from app.Http.Middleware.AuthMiddleware import require_auth

class MyController(Controller):
    @require_auth
    async def my_protected_route(self, request):
        # Only authenticated users can access
        return {"message": "Protected content"}
```

**Auto-redirect**:
- API requests → 401 JSON response
- Web requests → Redirect to `/login?redirect=/original-page`

### 4. Role-Based Access

Use the `@require_role()` decorator:

```python
from app.Http.Middleware.AuthMiddleware import require_role

class AdminController(Controller):
    @require_role('admin')
    async def admin_only(self, request):
        # Only admin users can access
        return {"message": "Admin content"}
```

**Roles**:
- `user` - Default role
- `admin` - Admin role

### 5. Get Current User

```python
from app.Http.Middleware.AuthMiddleware import get_current_user

async def my_handler(request):
    user = await get_current_user(request)
    
    if user:
        print(f"Logged in as: {user.name}")
        print(f"Role: {user.role}")
    else:
        print("Not authenticated")
```

### 6. Content Management

**Create Post with Image**:

```python
# In PostController.store()
form = await request.form()
title = form.get('title')
content = form.get('content')
image = form.get('featured_image')

# Upload image to storage
if image and image.filename:
    path = f"posts/{timestamp}_{image.filename}"
    Storage.put(path, await image.read())
    
# Create post
post = await Post.create_post(
    user_id=user.id,
    title=title,
    content=content,
    featured_image=path,
    status='published'
)
```

**Automatic Features**:
- Slug generation from title
- Excerpt from content (first 200 chars)
- Published timestamp on publish
- User ownership validation

## Routes

### Public Routes

| Method | Path | Controller | Description |
|--------|------|------------|-------------|
| GET | `/` | WelcomeController@index | Homepage |
| GET | `/login` | AuthController@show_login | Login form |
| POST | `/login` | AuthController@login | Login handler |
| GET | `/register` | AuthController@show_register | Register form |
| POST | `/register` | AuthController@register | Register handler |

### Protected Routes (Require Authentication)

| Method | Path | Controller | Description |
|--------|------|------------|-------------|
| GET | `/logout` | AuthController@logout | Logout |
| GET | `/profile` | AuthController@profile | User profile |
| GET | `/dashboard` | DashboardController@index | Dashboard |
| GET | `/posts` | PostController@index | List posts |
| GET | `/posts/create` | PostController@create | Create form |
| POST | `/posts` | PostController@store | Save post |
| GET | `/posts/:id/edit` | PostController@edit | Edit form |
| POST | `/posts/:id` | PostController@update | Update post |
| POST | `/posts/:id/delete` | PostController@destroy | Delete post |

## Views

### Layout System

**Base Layout** (`resources/views/layouts/app.html`):
- Navbar with auth status
- Navigation links
- User menu
- Responsive design

**Extending Layout**:
```html
{% extends "layouts/app.html" %}

{% block title %}My Page{% endblock %}

{% block content %}
    <h1>My Content</h1>
{% endblock %}
```

### Available Views

1. **Auth Views**:
   - `auth/login.html` - Login form
   - `auth/register.html` - Registration form

2. **Dashboard Views**:
   - `dashboard/index.html` - Dashboard with stats

3. **Post Views**:
   - `posts/index.html` - List posts
   - `posts/create.html` - Create post form
   - `posts/edit.html` - Edit post form

4. **Welcome**:
   - `welcome.html` - Homepage (shows different content for auth/guest)

## Security

### Password Hashing

Passwords are hashed using bcrypt:

```python
# Hash password (automatically done in User.create_user())
hashed = User.hash_password("plain_password")

# Verify password
is_valid = user.verify_password("plain_password")
```

### JWT Secret Key

**IMPORTANT**: Change the `SECRET_KEY` in `.env` for production!

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
SECRET_KEY=your-generated-secure-key
```

### Cookie Security

Cookies are set with:
- `httponly=True` - Prevents JavaScript access
- `samesite='lax'` - CSRF protection
- `max_age=86400` - 24 hour expiration

### HTTPS in Production

For production, update cookie settings in `AuthController`:

```python
response.set_cookie(
    key='auth_token',
    value=token,
    httponly=True,
    secure=True,  # Require HTTPS
    samesite='lax',
    max_age=86400
)
```

## Examples

### Example 1: Custom Protected Page

```python
# app/Http/Controllers/MyController.py
from app.Http.Controllers.Controller import Controller
from app.Http.Middleware.AuthMiddleware import require_auth, get_current_user

class MyController(Controller):
    @require_auth
    async def my_page(self, request):
        user = await get_current_user(request)
        
        return self.view('my_page', request, {
            'user': user,
            'message': f'Hello, {user.name}!'
        })
```

### Example 2: Admin-Only Route

```python
from app.Http.Middleware.AuthMiddleware import require_role

class AdminController(Controller):
    @require_role('admin')
    async def manage_users(self, request):
        users = await User.all()
        return self.view('admin.users', request, {'users': users})
```

### Example 3: API Authentication

```python
class ApiController(Controller):
    async def api_endpoint(self, request):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        # Format: "Bearer <token>"
        
        if not getattr(request.state, 'authenticated', False):
            return JSONResponse(
                {'error': 'Unauthorized'},
                status_code=401
            )
        
        user_data = request.state.user
        return {
            'user_id': user_data['user_id'],
            'email': user_data['email']
        }
```

### Example 4: User's Own Content

```python
class MyPostsController(Controller):
    @require_auth
    async def index(self, request):
        user = await get_current_user(request)
        
        # Get only user's own posts
        posts = await Post.where('user_id', user.id).get()
        
        return self.view('my_posts', request, {
            'user': user,
            'posts': posts
        })
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Table

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,
    featured_image VARCHAR(500),
    status VARCHAR(50) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Deployment

### Environment Variables

Make sure to set in production:

```bash
# .env
SECRET_KEY=your-secure-generated-key
FILESYSTEM_DISK=supabase  # or r2, for image uploads
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-key
SUPABASE_BUCKET=larathon
```

### Vercel Configuration

Update `vercel.json` environment variables:

```json
{
  "env": {
    "SECRET_KEY": "your-secure-key",
    "FILESYSTEM_DISK": "supabase",
    "SUPABASE_URL": "https://xxx.supabase.co",
    "SUPABASE_KEY": "your-key",
    "SUPABASE_BUCKET": "larathon"
  }
}
```

Or set via Vercel Dashboard → Project Settings → Environment Variables.

## Troubleshooting

### "Invalid token" errors

- Check `SECRET_KEY` is same on all instances
- Token may be expired (24 hour default)
- Clear cookies and login again

### "User not found" errors

- Run migrations: `python artisan.py migrate`
- Check database connection in `.env`

### Protected routes not working

- Make sure `AuthMiddleware` is registered in `bootstrap/providers.py`
- Check decorator is `@require_auth` not `require_auth`
- Controller method must be `async`

### Images not uploading

- Check `FILESYSTEM_DISK` is configured
- For Supabase: check bucket exists and is public
- Check storage permissions

## Summary

✅ **Complete auth system** - Registration, login, logout, profile
✅ **JWT-based** - Secure, stateless authentication
✅ **Protected routes** - Easy middleware decorators
✅ **Role-based access** - User/admin roles
✅ **Content management** - Full CRUD with images
✅ **Dashboard** - Beautiful UI with stats
✅ **Production-ready** - Secure, tested, documented

**Larathon is now a complete web application framework with authentication!** 🚀
