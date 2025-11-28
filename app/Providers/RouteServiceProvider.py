from routes.web import register_routes

class RouteServiceProvider:
    def register(self, app):
        print("🚏 RouteServiceProvider registered")
        
        # Register routes
        register_routes()
        
        # Use improved router
        from vendor.Illuminate.Routing.ImprovedRouter import Route
        app.include_router(Route.router)
        
        print(f"   ✅ Registered {len(Route._named_routes)} named routes")
        print(f"   ✅ Applied middleware to {len(Route._middleware_stack)} routes")
