"""
Post Model
"""
from vendor.Illuminate.Database.Model import Model
from datetime import datetime
import re


class Post(Model):
    """Post model for content management"""
    
    table = "posts"
    
    fillable = [
        "user_id",
        "title",
        "slug",
        "content",
        "excerpt",
        "featured_image",
        "status",
        "published_at"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @staticmethod
    def generate_slug(title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    @classmethod
    async def create_post(cls, user_id: int, title: str, content: str, **kwargs):
        """Create a new post with auto-generated slug"""
        slug = kwargs.get('slug') or cls.generate_slug(title)
        
        # Ensure unique slug
        counter = 1
        original_slug = slug
        while await cls.where('slug', slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        data = {
            'user_id': user_id,
            'title': title,
            'slug': slug,
            'content': content,
            'excerpt': kwargs.get('excerpt', content[:200] if content else ''),
            'featured_image': kwargs.get('featured_image'),
            'status': kwargs.get('status', 'draft')
        }
        
        if kwargs.get('status') == 'published' and not kwargs.get('published_at'):
            data['published_at'] = datetime.now()
        
        return await cls.create(data)
    
    async def author(self):
        """Get the author of this post"""
        from app.Models.User import User
        return await User.find(self.user_id)
    
    @classmethod
    async def published(cls):
        """Get only published posts"""
        return await cls.where('status', 'published').order_by('published_at', 'desc')
    
    @classmethod
    async def drafts(cls):
        """Get only draft posts"""
        return await cls.where('status', 'draft').order_by('created_at', 'desc')
    
    @classmethod
    async def by_user(cls, user_id: int):
        """Get posts by specific user"""
        return await cls.where('user_id', user_id).order_by('created_at', 'desc')
    
    def is_published(self) -> bool:
        """Check if post is published"""
        return self.status == 'published'
    
    def is_draft(self) -> bool:
        """Check if post is draft"""
        return self.status == 'draft'
