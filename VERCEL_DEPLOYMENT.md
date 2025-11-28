# Vercel Deployment Guide - FastAPI Native Support

## ✅ Issue RESOLVED: TypeError: issubclass() arg 1 must be a class

### The Problem
```
TypeError: issubclass() arg 1 must be a class
```
This error occurred because we were using **Mangum** (ASGI adapter), but **Vercel has native FastAPI support** and doesn't need any wrapper!

### The Solution
**Export FastAPI app directly** - Vercel automatically detects and runs it.

```python
# ✅ CORRECT - What we do now
app = create_app()

# ❌ WRONG - What caused the error
from mangum import Mangum
handler = Mangum(app)  # Don't do this on Vercel!
```

## Current Configuration

### File: api/index.py (end of file)
```python
# ================================================================================
# Application Entry Point for Vercel
# ================================================================================

# Vercel automatically detects and runs FastAPI apps
# Export 'app' instance directly - no wrapper needed
app = create_app()
```

### File: vercel.json
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

## How Vercel Detects FastAPI

Vercel's Python runtime automatically looks for a FastAPI instance named `app` in these locations:
- ✅ `api/index.py` ← We use this!
- `app.py`
- `server.py`
- `src/index.py`
- `src/app.py`
- `src/server.py`
- `app/index.py`
- `app/app.py`
- `app/server.py`

**No configuration needed** - just export `app`!

## Build & Deploy Process

### 1. Build
```bash
python artisan.py build
```

This creates:
- ✅ `api/index.py` - Bundled FastAPI app (32KB, ~860 lines)
- ✅ `api/requirements.txt` - All dependencies
- ✅ `api/resources/views/` - All templates
- ✅ `api/public/static/` - Static assets

### 2. Verify Locally
```bash
cd api
python -c "import sys; sys.path.insert(0, '..'); import index; print('✅ OK')"
```

Expected output:
```
🔧 AppServiceProvider registered
🔑 AuthServiceProvider registered
✅ OK
```

### 3. Deploy
```bash
vercel --prod
```

## Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

```
DB_CONNECTION=pgsql
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=6543
DB_DATABASE=postgres
DB_USERNAME=postgres.xxxxx
DB_PASSWORD=your-password
SECRET_KEY=your-secret-key
```

## What Changed

### Before (WRONG ❌)
```python
# api/index.py
from mangum import Mangum
_app = create_app()
handler = Mangum(_app, lifespan="off")  # Caused TypeError!
app = _app
```

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [...]
}
```

### After (CORRECT ✅)
```python
# api/index.py
app = create_app()  # Direct export - Vercel auto-detects!
```

```json
// vercel.json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

## Key Learnings

1. **Vercel has native FastAPI support** - No ASGI adapter needed
2. **Just export `app`** - Vercel finds it automatically
3. **Simple vercel.json** - Use `rewrites`, not complex `builds`/`routes`
4. **Mangum is for AWS Lambda** - Not needed for Vercel

## Troubleshooting

### If you still see the TypeError:
1. Check `api/index.py` - Should end with: `app = create_app()`
2. No `Mangum` import should exist in the file
3. Rebuild: `python artisan.py build`
4. Redeploy: `vercel --prod`

### If app doesn't start:
1. Check Vercel logs for errors
2. Verify environment variables are set
3. Test locally first: `cd api && uvicorn index:app`

### If routes don't work:
1. Check `vercel.json` has correct rewrites
2. Verify `api/index.py` exists and exports `app`

## Testing Deployment

After deployment:
1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Should see your welcome page
3. Test routes: `/todos`, `/test`
4. Check Vercel logs for any errors

## Success Indicators

✅ Build completes without errors
✅ Bundle exports: `app = create_app()`
✅ No Mangum import in bundle
✅ vercel.json uses simple rewrites
✅ App type is FastAPI (not Mangum)
✅ Vercel deployment succeeds
✅ Application loads in browser
✅ Routes work correctly

## Additional Resources

- [Vercel FastAPI Documentation](https://vercel.com/docs/frameworks/fastapi)
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- Project docs: `BUILD_GUIDE.md`, `DEPLOYMENT_FIXES.md`

## Summary

**The error was caused by using Mangum** - which is only needed for AWS Lambda, not Vercel. **Vercel has native FastAPI support** and just needs a plain `app` export.

**Now configured correctly:**
- ✅ Direct FastAPI export
- ✅ No Mangum wrapper
- ✅ Simple vercel.json
- ✅ Ready for deployment!

Run `python artisan.py build && vercel --prod` and your app should deploy successfully! 🚀
