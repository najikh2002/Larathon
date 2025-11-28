from vendor.Illuminate.Routing.Router import Router
from vendor.Illuminate.Support.Facades.Route import Route
from routes.web import register_routes

class RouteServiceProvider:
    def register(self, app):
        # buat instance Router
        router_instance = Router()

        # swap ke facade
        Route.swap(router_instance)

        # load definisi routes
        register_routes()

        # setelah semua route terdaftar, baru include ke FastAPI
        app.include_router(router_instance.router)
