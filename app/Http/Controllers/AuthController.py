"""
Authentication Controller
"""
from app.Http.Controllers.Controller import Controller
from app.Models.User import User
from vendor.Illuminate.Auth.JWT import JWT
from starlette.responses import JSONResponse, RedirectResponse


class AuthController(Controller):
    """Handle user authentication"""
    
    def show_login(self, request):
        """Show login form"""
        if getattr(request.state, 'authenticated', False):
            return RedirectResponse(url='/dashboard', status_code=302)
        
        redirect_to = request.query_params.get('redirect', '/dashboard')
        return self.view('auth.login', request, {'redirect_to': redirect_to})
    
    def show_register(self, request):
        """Show registration form"""
        if getattr(request.state, 'authenticated', False):
            return RedirectResponse(url='/dashboard', status_code=302)
        
        return self.view('auth.register', request)
    
    async def register(self, request):
        """Handle user registration"""
        try:
            form = await request.form()
            name = form.get('name', '').strip()
            email = form.get('email', '').strip().lower()
            password = form.get('password', '')
            password_confirm = form.get('password_confirm', '')
            
            # Validation
            errors = []
            if not name or len(name) < 2:
                errors.append('Name must be at least 2 characters')
            if not email or '@' not in email:
                errors.append('Valid email is required')
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters')
            if password != password_confirm:
                errors.append('Passwords do not match')
            
            # Check if email exists
            existing_user = await User.find_by_email(email)
            if existing_user:
                errors.append('Email already registered')
            
            if errors:
                return self.view('auth.register', request, {
                    'errors': errors,
                    'name': name,
                    'email': email
                })
            
            # Create user
            user = await User.create_user(name, email, password)
            
            # Generate token
            token = JWT.generate(user.id, user.email, user.role)
            
            # Set cookie and redirect
            response = RedirectResponse(url='/dashboard', status_code=302)
            response.set_cookie(
                key='auth_token',
                value=token,
                httponly=True,
                max_age=86400,  # 24 hours
                samesite='lax'
            )
            return response
            
        except Exception as e:
            return self.view('auth.register', request, {
                'errors': [f'Registration failed: {str(e)}']
            })
    
    async def login(self, request):
        """Handle user login"""
        try:
            # Get form data from cache (set by MethodOverrideMiddleware)
            # or read fresh if not cached
            if hasattr(request.state, '_cached_form'):
                form = request.state._cached_form
                print(f"DEBUG: Using cached form data: {dict(form)}")
            else:
                form = await request.form()
                print(f"DEBUG: Form data read fresh: {dict(form)}")
            
            email = form.get('email', '').strip().lower()
            password = form.get('password', '')
            redirect_to = form.get('redirect_to', '/dashboard')
            
            print(f"DEBUG: Email={email}, Password={'*' * len(password) if password else 'EMPTY'}, Redirect={redirect_to}")
            
            # Validation
            if not email or not password:
                return self.view('auth.login', request, {
                    'error': 'Email and password are required',
                    'email': email,
                    'redirect_to': redirect_to
                })
            
            # Find user
            user = await User.find_by_email(email)
            
            if not user or not user.verify_password(password):
                return self.view('auth.login', request, {
                    'error': 'Invalid email or password',
                    'email': email,
                    'redirect_to': redirect_to
                })
            
            if not user.is_active:
                return self.view('auth.login', request, {
                    'error': 'Account is disabled',
                    'email': email,
                    'redirect_to': redirect_to
                })
            
            # Generate token
            token = JWT.generate(user.id, user.email, user.role)
            
            # Set cookie and redirect
            response = RedirectResponse(url=redirect_to, status_code=302)
            response.set_cookie(
                key='auth_token',
                value=token,
                httponly=True,
                max_age=86400,  # 24 hours
                samesite='lax'
            )
            return response
            
        except Exception as e:
            return self.view('auth.login', request, {
                'error': f'Login failed: {str(e)}',
                'redirect_to': redirect_to
            })
    
    def logout(self, request):
        """Handle user logout"""
        response = RedirectResponse(url='/', status_code=302)
        response.delete_cookie('auth_token')
        return response
    
    async def profile(self, request):
        """Show user profile"""
        from app.Http.Middleware.AuthMiddleware import get_current_user
        
        user = await get_current_user(request)
        if not user:
            return RedirectResponse(url='/login', status_code=302)
        
        return self.view('auth.profile', request, {'user': user})
