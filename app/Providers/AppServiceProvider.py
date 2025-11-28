from app.Http.Middleware.MethodOverrideMiddleware import MethodOverrideMiddleware
from app.Http.Middleware.AuthMiddleware import AuthMiddleware

class AppServiceProvider:
    def register(self, app):
        print("🔧 AppServiceProvider registered")
        # Register middleware
        app.add_middleware(MethodOverrideMiddleware)
        app.add_middleware(AuthMiddleware)

    def boot(self, app):
        print("🚀 AppServiceProvider booted")
