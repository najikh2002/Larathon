from fastapi import FastAPI
from bootstrap.providers import register_providers
from fastapi.staticfiles import StaticFiles
import os

def create_app():
    app = FastAPI()

    register_providers(app)

    # MOUNT STATIC FILES - try multiple possible locations
    _current_file_dir = os.path.dirname(os.path.abspath(__file__))
    _possible_static_paths = [
        os.path.join(_current_file_dir, "public", "static"),     # api/public/static
        os.path.join(os.getcwd(), "api", "public", "static"),    # /var/task/api/public/static
        os.path.join(os.getcwd(), "public", "static"),           # /var/task/public/static
        "public/static",                                          # relative fallback
    ]

    static_dir = None
    for path in _possible_static_paths:
        if os.path.exists(path) and os.path.isdir(path):
            static_dir = path
            break

    if static_dir:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


# Don't create app instance at module level - let the entry point handle it
# This prevents issues with bundling and allows proper initialization order
