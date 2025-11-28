# vendor/Illuminate/View/View.py
from starlette.templating import Jinja2Templates
import os

# Try multiple possible template locations for Vercel compatibility
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_possible_paths = [
    os.path.join(_current_file_dir, "resources", "views"),     # local: vendor/Illuminate/View/resources/views
    os.path.join(os.getcwd(), "api", "resources", "views"),    # Vercel: /var/task/api/resources/views
    os.path.join(os.getcwd(), "resources", "views"),           # local: /project/resources/views
    "api/resources/views",                                      # relative with api prefix
    "resources/views",                                          # relative fallback
]

VIEWS_DIR = None
for path in _possible_paths:
    if os.path.exists(path):
        VIEWS_DIR = path
        break

if VIEWS_DIR is None:
    # Last resort: try api/resources/views (Vercel serverless)
    VIEWS_DIR = "api/resources/views"

templates = Jinja2Templates(directory=VIEWS_DIR)

class View:
    @staticmethod
    def make(template: str, context: dict = None):
        # default kosong
        context = context or {}
        if "request" not in context:
            raise ValueError('View.make() requires "request" in context')
        return templates.TemplateResponse(template.replace(".", "/") + ".html", context)
