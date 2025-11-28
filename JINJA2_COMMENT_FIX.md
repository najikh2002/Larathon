# Jinja2 Comment Fix - Static Route Error

## Issue
```
starlette.routing.NoMatchFound: No route exists for name "static" and params "path".
```

Error occurred at line 10 of `welcome.html`:
```html
<!-- <img src="{{ request.url_for('static', path='larathon.png') }}" alt="Gambar" width="200px"> -->
```

## Root Cause

**HTML comments don't hide Jinja2 template code!**

```html
<!-- {{ this_still_gets_processed }} -->  ❌ WRONG
```

When Jinja2 renders a template:
1. **First**: Process Jinja2 syntax (`{{ }}`, `{% %}`, `{# #}`)
2. **Then**: Output HTML (including HTML comments `<!-- -->`)

So even though the `<img>` tag was in an HTML comment, Jinja2 still tried to execute:
```python
request.url_for('static', path='larathon.png')
```

This failed because:
- The `static` route wasn't properly mounted
- Or the route name wasn't registered as "static"

## Solution

### Use Jinja2 Comments Instead

```html
{# This is a Jinja2 comment - completely ignored #}
{# <img src="{{ request.url_for('static', path='larathon.png') }}"> #}
```

**Jinja2 comments** `{# #}`:
- ✅ Are removed during template compilation
- ✅ Don't appear in output HTML
- ✅ Don't execute any code inside them
- ✅ Perfect for commenting out Jinja2 expressions

**HTML comments** `<!-- -->`:
- ❌ Still execute Jinja2 code inside them
- ❌ Appear in output HTML
- ❌ Only hide from browser rendering

## The Fix

### Before (WRONG)
```html
<!-- <img src="{{ request.url_for('static', path='larathon.png') }}" alt="Gambar" width="200px"> -->
```
- HTML comment
- Jinja2 still executes `request.url_for()`
- Causes NoMatchFound error

### After (CORRECT)
```html
{# <img src="{{ request.url_for('static', path='larathon.png') }}" alt="Gambar" width="200px"> #}
```
- Jinja2 comment
- Code is completely ignored
- No error

## Updated Template

File: `resources/views/welcome.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Larathon</title>
    <link rel="stylesheet" href="/css/app.css">
</head>
<body>
    <div style="text-align: center; margin-top: 100px;">
        {# <img src="{{ request.url_for('static', path='larathon.png') }}" alt="Gambar" width="200px"> #}
        <h1>Welcome to Larathon 🚀</h1>
        <p>This is the default landing page.</p>
        <p><a href="/todos" style="color: #667eea; text-decoration: none;">Go to Todos →</a></p>

        <footer style="margin-top: 50px; color: #666;">
            <p>Created by <strong>Hizbullah Najihan</strong></p>
            <p>
                <a href="https://github.com/najikh2002" target="_blank" style="color: #667eea;">GitHub</a> |
                <a href="https://linkedin.com/in/hizbullah-najihan" target="_blank" style="color: #667eea;">LinkedIn</a>
            </p>
        </footer>
    </div>
</body>
</html>
```

## Jinja2 Comment Types

### 1. Single-line Comment
```jinja2
{# This is a comment #}
```

### 2. Multi-line Comment
```jinja2
{#
    This is a
    multi-line
    comment
#}
```

### 3. Inline Comment
```jinja2
<p>{{ user.name }} {# Display username #} </p>
```

## Common Mistake

```html
<!-- Trying to hide this: {{ variable }} -->  ❌ Variable still rendered!
{# Actually hiding this: {{ variable }} #}    ✅ Variable NOT rendered
```

## When to Use Each

### HTML Comments `<!-- -->`
Use when you want:
- Comment visible in browser's View Source
- Comment in final HTML output
- No Jinja2 code inside

```html
<!-- This note appears in HTML source -->
<p>Content</p>
```

### Jinja2 Comments `{# #}`
Use when you want:
- Comment NOT in output HTML
- Disable Jinja2 code temporarily
- Development/debugging notes

```jinja2
{# TODO: Add pagination here #}
{# {% for item in items %} ... {% endfor %} #}
```

## Testing

After fix, rebuild and deploy:

```bash
# Rebuild with fixed template
python artisan.py build

# Verify comment is Jinja2 style
grep '{#.*url_for.*#}' api/resources/views/welcome.html

# Deploy
vercel --prod
```

## Summary

**Problem**: HTML comment `<!-- -->` doesn't prevent Jinja2 from executing `{{ }}` code
**Solution**: Use Jinja2 comment `{# #}` to truly disable template code

This is a **critical difference** to remember when working with Jinja2 templates!

## Related Issues Fixed

1. ✅ TypeError: issubclass() - Removed Mangum
2. ✅ TemplateNotFound - Dynamic path detection
3. ✅ NoMatchFound: static route - Fixed Jinja2 comment

All issues resolved! 🚀
