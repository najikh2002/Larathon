"""
Post Controller
"""
from app.Http.Controllers.Controller import Controller
from app.Http.Middleware.AuthMiddleware import require_auth, get_current_user
from app.Models.Post import Post
from vendor.Illuminate.Filesystem.Storage import Storage
from starlette.responses import RedirectResponse
import os
from datetime import datetime


class PostController(Controller):
    """Handle post/content CRUD operations"""
    
    @require_auth
    async def index(self, request):
        """List all posts for current user"""
        user = await get_current_user(request)
        posts = await Post.by_user(user.id).get()
        
        return self.view('posts.index', request, {
            'user': user,
            'posts': posts
        })
    
    @require_auth
    async def create(self, request):
        """Show create post form"""
        user = await get_current_user(request)
        return self.view('posts.create', request, {'user': user})
    
    @require_auth
    async def store(self, request):
        """Store new post"""
        user = await get_current_user(request)
        
        try:
            form = await request.form()
            title = form.get('title', '').strip()
            content = form.get('content', '').strip()
            excerpt = form.get('excerpt', '').strip()
            status = form.get('status', 'draft')
            featured_image_file = form.get('featured_image')
            
            # Debug logging
            print(f"Form data received - Title: {title}, Status: {status}")
            print(f"Featured image file: {featured_image_file}, Type: {type(featured_image_file)}")
            
            # Validation
            if not title:
                return self.view('posts.create', request, {
                    'user': user,
                    'error': 'Title is required',
                    'title': title,
                    'content': content
                })
            
            # Handle featured image upload
            featured_image_path = None
            if featured_image_file:
                # Check if it's actually a file (not just empty form field)
                if hasattr(featured_image_file, 'filename') and featured_image_file.filename:
                    print(f"Processing image: {featured_image_file.filename}")
                    
                    # Generate unique filename
                    ext = os.path.splitext(featured_image_file.filename)[1]
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"post_{timestamp}{ext}"
                    path = f"posts/{filename}"
                    
                    # Upload to storage
                    file_content = await featured_image_file.read()
                    
                    if file_content:  # Only upload if not empty
                        Storage.put(path, file_content)
                        featured_image_path = path
                        print(f"Image uploaded to: {path}")
                    else:
                        print("Image file is empty, skipping upload")
                else:
                    print("No filename or empty file field")
            
            # Create post
            post = await Post.create_post(
                user_id=user.id,
                title=title,
                content=content,
                excerpt=excerpt or (content[:200] if content else ''),
                featured_image=featured_image_path,
                status=status
            )
            
            print(f"Post created with ID: {post.id}")
            
            return RedirectResponse(url='/posts', status_code=302)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error creating post: {error_trace}")
            
            return self.view('posts.create', request, {
                'user': user,
                'error': f'Failed to create post: {str(e)}'
            })
    
    @require_auth
    async def show(self, request, post_id: int):
        """Show single post"""
        user = await get_current_user(request)
        post = await Post.find(post_id)
        
        if not post:
            return RedirectResponse(url='/posts', status_code=302)
        
        # Check ownership
        if post.user_id != user.id:
            return RedirectResponse(url='/posts', status_code=302)
        
        return self.view('posts.show', request, {
            'user': user,
            'post': post
        })
    
    @require_auth
    async def edit(self, request, post_id: int):
        """Show edit post form"""
        user = await get_current_user(request)
        post = await Post.find(post_id)
        
        if not post or post.user_id != user.id:
            return RedirectResponse(url='/posts', status_code=302)
        
        return self.view('posts.edit', request, {
            'user': user,
            'post': post
        })
    
    @require_auth
    async def update(self, request, post_id: int):
        """Update existing post"""
        user = await get_current_user(request)
        post = await Post.find(post_id)
        
        if not post or post.user_id != user.id:
            return RedirectResponse(url='/posts', status_code=302)
        
        try:
            form = await request.form()
            title = form.get('title', '').strip()
            content = form.get('content', '').strip()
            excerpt = form.get('excerpt', '').strip()
            status = form.get('status', 'draft')
            featured_image_file = form.get('featured_image')
            
            # Validation
            if not title:
                return self.view('posts.edit', request, {
                    'user': user,
                    'post': post,
                    'error': 'Title is required'
                })
            
            # Handle featured image upload
            if featured_image_file and hasattr(featured_image_file, 'filename') and featured_image_file.filename:
                # Delete old image
                if post.featured_image:
                    try:
                        Storage.delete(post.featured_image)
                    except:
                        pass
                
                # Upload new image
                ext = os.path.splitext(featured_image_file.filename)[1]
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"post_{timestamp}{ext}"
                path = f"posts/{filename}"
                
                file_content = await featured_image_file.read()
                Storage.put(path, file_content)
                post.featured_image = path
            
            # Update post
            post.title = title
            post.slug = Post.generate_slug(title)
            post.content = content
            post.excerpt = excerpt or (content[:200] if content else '')
            post.status = status
            
            if status == 'published' and not post.published_at:
                post.published_at = datetime.now()
            
            await post.save()
            
            return RedirectResponse(url='/posts', status_code=302)
            
        except Exception as e:
            return self.view('posts.edit', request, {
                'user': user,
                'post': post,
                'error': f'Failed to update post: {str(e)}'
            })
    
    @require_auth
    async def destroy(self, request, post_id: int):
        """Delete post"""
        user = await get_current_user(request)
        post = await Post.find(post_id)
        
        if not post or post.user_id != user.id:
            return RedirectResponse(url='/posts', status_code=302)
        
        # Delete featured image if exists
        if post.featured_image:
            try:
                Storage.delete(post.featured_image)
            except:
                pass
        
        # Delete post
        await post.delete()
        
        return RedirectResponse(url='/posts', status_code=302)
