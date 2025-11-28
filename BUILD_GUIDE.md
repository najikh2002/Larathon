# Larathon Build & Deployment Guide

## Overview
Larathon uses a custom bundler to prepare the application for serverless deployment on Vercel. The bundler automatically handles code bundling, resource copying, and deployment preparation.

## What the Bundler Does

### 1. **Python Code Bundling**
- Bundles all Python files from: `app/`, `config/`, `bootstrap/`, `vendor/`, `database/`, `routes/`
- Combines them into a single `api/index.py` file
- Removes local imports and consolidates external dependencies
- Maintains proper execution order
- **Exports FastAPI app directly** - Vercel detects it automatically

### 2. **Resource Management**
- **Views/Templates**: Automatically copies `resources/views/` → `api/resources/views/`
- **Static Files**: Automatically copies `public/static/` → `api/public/static/`
- **Dependencies**: Automatically copies `requirements.txt` → `api/requirements.txt`
- Ensures all HTML templates and assets are available in serverless environment

### 3. **Vercel Native Support**
- Exports FastAPI `app` instance directly
- Vercel automatically detects and runs FastAPI apps (no wrapper needed)
- Uses Vercel's built-in Python runtime with native ASGI support

### 4. **Vercel Configuration**
- Creates/updates `vercel.json` with proper routes and build settings
- Creates `.vercelignore` to exclude unnecessary files from deployment

## Requirements

The bundler requires these key dependencies (automatically included):
- **FastAPI**: Web framework (Vercel has native support!)
- **SQLAlchemy**: Database ORM
- **Jinja2**: Template engine
- **psycopg2-binary**: PostgreSQL driver
- **python-dotenv**: Environment variables

All dependencies are in `requirements.txt` and automatically copied to `api/` during build.

**Note**: Vercel has **native FastAPI support** - no ASGI adapter needed!

## How to Build for Deployment

### Step 1: Build the Application
```bash
python artisan.py build
```

This command will:
- ✅ Bundle all Python code into `api/index.py`
- ✅ Copy all views from `resources/views/` to `api/resources/views/`
- ✅ Copy static files from `public/static/` to `api/public/static/`
- ✅ Generate deployment configuration files

### Step 2: Verify the Build
After building, check that:
- `api/index.py` exists and contains your bundled code
- `api/resources/views/` contains all your HTML templates
- `api/public/static/` contains all static assets

```bash
# Check bundle size
ls -lh api/index.py

# Verify views
find api/resources/views -name "*.html"

# Verify static files
ls -la api/public/static/
```

### Step 3: Deploy to Vercel

#### First Time Setup
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

#### Set Environment Variables in Vercel
Go to your Vercel project settings and add:
- `DB_CONNECTION=pgsql`
- `DB_HOST=<your-supabase-host>`
- `DB_PORT=6543`
- `DB_DATABASE=postgres`
- `DB_USERNAME=<your-username>`
- `DB_PASSWORD=<your-password>`
- `SECRET_KEY=<your-secret-key>`

#### Deploy
```bash
# Deploy to production
vercel --prod
```

## Adding New Pages - Workflow

When you add a new page/controller, follow this workflow:

### 1. Create the View (HTML Template)
```bash
# Example: Create a new page
touch resources/views/about.html
```

### 2. Create the Controller
```bash
python artisan.py make:controller AboutController
```

### 3. Add Route
Edit `routes/web.py`:
```python
from app.Http.Controllers.AboutController import AboutController

Route.get("/about", AboutController, "index")
```

### 4. Implement Controller Method
Edit `app/Http/Controllers/AboutController.py`:
```python
class AboutController(Controller):
    def index(self, request):
        return self.view("about", request)
```

### 5. **Build and Deploy**
```bash
# Build (this will include your new page automatically)
python artisan.py build

# Deploy
vercel --prod
```

**Important**: The bundler will automatically include:
- ✅ Your new controller in the bundle
- ✅ Your new view in `api/resources/views/`
- ✅ Any new routes you defined

## Testing Locally Before Deployment

### Test with Local Server
```bash
python artisan.py serve
```

Visit `http://127.0.0.1:8000` to test your application locally.

### Test the Bundled Version
To test the exact code that will be deployed:
```bash
# Build first
python artisan.py build

# Run uvicorn directly on the bundled file
cd api
uvicorn index:app --reload
```

## Troubleshooting

### View Not Found Error
**Problem**: Template not found in Vercel deployment

**Solution**: Run `python artisan.py build` to ensure views are copied to `api/resources/views/`

### Missing Static Files
**Problem**: CSS/JS/Images not loading

**Solution**: 
1. Ensure files are in `public/static/`
2. Run `python artisan.py build`
3. Verify files copied to `api/public/static/`

### Import Errors
**Problem**: Module not found errors

**Solution**: Ensure all dependencies are in `requirements.txt` and installed in Vercel

## Build Artifacts Structure

After running `python artisan.py build`, you should have:

```
api/
├── index.py              # Bundled Python code
├── requirements.txt      # Python dependencies
├── resources/
│   └── views/           # All HTML templates
│       ├── welcome.html
│       ├── test.html
│       └── todos/
│           ├── index.html
│           ├── create.html
│           ├── edit.html
│           └── show.html
└── public/
    └── static/          # Static assets
        └── larathon.png
```

## Best Practices

1. **Always build before deploying**: Run `python artisan.py build` before each deployment
2. **Test locally first**: Use `python artisan.py serve` to test changes before building
3. **Check build output**: Verify that your new files are included in the bundle
4. **Use relative paths**: In templates, use relative paths for static files
5. **Environment variables**: Never commit `.env` file, use Vercel environment variables
6. **Database migrations**: Run migrations manually in production (Vercel doesn't auto-migrate)

## Continuous Deployment

For automatic deployments, connect your Git repository to Vercel:
1. Push to main branch
2. Vercel automatically runs build
3. Deployment happens automatically

**Note**: Ensure `vercel.json` and `.vercelignore` are committed to your repository.

## Common Issues & Solutions

### Issue: NameError in Vercel deployment

**Problem**: `NameError: name 'os' is not defined` or similar import errors

**Cause**: Missing imports in bundled file

**Solution**: Bundler now automatically preserves all external imports. Run `python artisan.py build` to regenerate the bundle with proper imports.

### Issue: TypeError: issubclass() arg 1 must be a class

**Problem**: `TypeError: issubclass() arg 1 must be a class` in Vercel deployment logs

**Cause**: Using unnecessary ASGI adapters (like Mangum) when Vercel has native FastAPI support

**Solution**: Export FastAPI app directly without any wrapper:
```python
# ✅ Correct - Direct export
app = FastAPI()

# ❌ Wrong - Don't use Mangum or other wrappers
handler = Mangum(app)  # Not needed for Vercel!
```

The bundler now exports `app` directly, and Vercel's Python runtime automatically detects and runs it.

### Issue: Function/Class not defined

**Problem**: `NameError: name 'SomeFunction' is not defined`

**Cause**: Incorrect file ordering in bundle or top-level code execution

**Solution**: 
- Avoid executing code at module/file top-level
- Use functions and call them from proper entry points
- Check that imports are using full paths (e.g., `from config.database import get_engine` not `from vendor.Illuminate.Console import database`)

### Issue: Routes not working

**Problem**: Routes defined but not accessible

**Solution**: Routes should be defined in a function in `routes/web.py` and called by `RouteServiceProvider`, not executed at top-level.

## Architecture Notes

### How Bundling Works

1. **Collection**: Collects all `.py` files from `app/`, `config/`, `bootstrap/`, `vendor/`, `database/`, `routes/`
2. **Import Extraction**: Identifies external imports (FastAPI, SQLAlchemy, etc.) vs local imports
3. **Code Processing**: Removes local imports, keeps external imports
4. **Ordering**: Processes files in dependency order: config → vendor → database → app → bootstrap → routes
5. **Assembly**: Combines all code into single file with external imports at top
6. **Resources**: Copies views and static files to deployment locations

### File Exclusions

The bundler excludes:
- `__pycache__/` and `.pyc` files
- `tests/` directory
- `artisan.py` (CLI tool)
- Build tools: `bundler.py`, `generators.py`
- `vendor/Illuminate/Console/database.py` (migrate commands, not needed in serverless)
- `Commands/` directory (CLI commands)
- `migrations/` directory (migration files)
- `seeders/` directory (seeder files)

## Summary

The bundler is now fully configured to:
- ✅ Bundle all Python code with proper import handling
- ✅ Copy all views automatically
- ✅ Copy all static files automatically
- ✅ Copy requirements.txt automatically
- ✅ Work with new pages without manual intervention
- ✅ Handle dependency ordering correctly
- ✅ Preserve external imports (os, sys, FastAPI, SQLAlchemy, etc.)
- ✅ Remove local imports to avoid conflicts
- ✅ **Export FastAPI app directly for Vercel native support**
- ✅ No unnecessary wrappers or adapters needed

**Just remember**: Run `python artisan.py build` before deployment, and everything will be included automatically! 🚀

### What Gets Built

After running `python artisan.py build`, you'll have:

```
api/
├── index.py              # Bundled FastAPI app (32KB, ~860 lines)
├── requirements.txt      # All dependencies
├── resources/
│   └── views/           # All your HTML templates
│       ├── welcome.html
│       ├── test.html
│       └── todos/
└── public/
    └── static/          # All static assets
```

**Key Export:**
```python
# api/index.py (end of file)
app = create_app()  # Vercel auto-detects this!
```

Vercel's Python runtime automatically finds and runs the `app` instance.

## Testing the Bundle

To verify your bundle works before deploying:

```bash
# Build the bundle
python artisan.py build

# Test import (should show no errors)
cd api && python -c "import sys; sys.path.insert(0, '..'); import index; print('✅ Success!')"

# Test with uvicorn
cd api && uvicorn index:app --reload
```

Visit `http://localhost:8000` - if your app loads, the bundle is ready for Vercel!
