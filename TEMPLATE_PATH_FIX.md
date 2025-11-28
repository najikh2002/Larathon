# Template Path Fix for Vercel Deployment

## Issue
```
jinja2.exceptions.TemplateNotFound: 'welcome.html' not found in search path: 'resources/views'
```

## Root Cause

In `vendor/Illuminate/View/View.py`, the templates path was hardcoded:
```python
# ❌ WRONG - Hardcoded path
templates = Jinja2Templates(directory="resources/views")
```

This worked locally but failed in Vercel because:
- **Local**: Working dir is project root, `resources/views` exists
- **Vercel**: Working dir is `/var/task/`, templates are at `/var/task/api/resources/views/`

The hardcoded relative path couldn't find templates in Vercel's directory structure.

## Solution

Updated `vendor/Illuminate/View/View.py` to detect template directory dynamically:

```python
import os
from starlette.templating import Jinja2Templates

# Try multiple possible template locations for Vercel compatibility
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_possible_paths = [
    os.path.join(_current_file_dir, "resources", "views"),     # Bundle dir: /var/task/api/resources/views
    os.path.join(os.getcwd(), "api", "resources", "views"),    # From working dir: /var/task/api/resources/views
    os.path.join(os.getcwd(), "resources", "views"),           # Local dev: /project/resources/views
    "api/resources/views",                                      # Relative with api prefix
    "resources/views",                                          # Relative fallback
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
```

## How It Works

### Local Development
- `__file__` = `/path/to/project/vendor/Illuminate/View/View.py`
- `_current_file_dir` = `/path/to/project/vendor/Illuminate/View/`
- Checks: `/path/to/project/vendor/Illuminate/View/resources/views` ❌
- Checks: `/path/to/project/api/resources/views` ✅ **FOUND!**
- `VIEWS_DIR` = `/path/to/project/api/resources/views`

### Vercel Serverless (After Build)
- `__file__` = `/var/task/api/index.py` (bundled file)
- `_current_file_dir` = `/var/task/api/`
- Checks: `/var/task/api/resources/views` ✅ **FOUND!**
- `VIEWS_DIR` = `/var/task/api/resources/views`
- Templates exist because bundler copies them there

## Directory Structure

### After Build (`python artisan.py build`)
```
api/
├── index.py              # Bundled FastAPI app
├── requirements.txt
├── resources/
│   └── views/           # Templates copied here ✓
│       ├── welcome.html
│       ├── test.html
│       └── todos/
│           ├── index.html
│           ├── create.html
│           ├── edit.html
│           └── show.html
└── public/
    └── static/          # Static files
```

### In Vercel (Deployed)
```
/var/task/
├── api/
│   ├── index.py         # Your bundle
│   ├── resources/
│   │   └── views/      # Templates here ✓
│   └── public/
│       └── static/
└── (Vercel runtime files)
```

## Path Detection Logic

1. **First check**: Relative to bundle file
   - Works in Vercel: `/var/task/api/` + `resources/views`
   - Finds: `/var/task/api/resources/views/` ✅

2. **Second check**: From working directory with api prefix
   - Fallback if first fails
   - `/var/task/` + `api/resources/views`

3. **Third check**: From working directory without prefix
   - For local development
   - `/project/` + `resources/views`

4. **Relative paths**: Last resort fallbacks

## Testing

### Local Test
```bash
cd /Users/hizbullahnajihan/Documents/Larathon
source env/bin/activate
cd api
python -c "import sys; sys.path.insert(0, '..'); import index; print('Views:', index.VIEWS_DIR)"
```

Expected output:
```
🔧 AppServiceProvider registered
🔑 AuthServiceProvider registered
Views: /Users/hizbullahnajihan/Documents/Larathon/api/resources/views
```

### Verify Templates Copied
```bash
find api/resources/views -name "*.html"
```

Should list all 6 templates including `welcome.html`.

## Deployment Steps

1. **Rebuild with fix**:
   ```bash
   python artisan.py build
   ```

2. **Verify templates**:
   ```bash
   ls api/resources/views/welcome.html  # Should exist
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Test**:
   - Visit your Vercel URL
   - Should load welcome page successfully
   - No more TemplateNotFound error

## What Was Fixed

- ✅ Dynamic path detection (works in both local and Vercel)
- ✅ Multiple fallback paths for reliability
- ✅ Uses `__file__` to find bundle location
- ✅ Prioritizes bundle-relative path (most reliable in Vercel)
- ✅ Templates automatically copied by bundler
- ✅ Works with Vercel's `/var/task/` directory structure

## Summary

**Before**: Hardcoded `"resources/views"` - only worked locally
**After**: Dynamic detection - works everywhere

The bundler already copies templates to `api/resources/views/`, now the View class can find them in Vercel's serverless environment.

**Deploy and the TemplateNotFound error should be resolved!** 🚀
