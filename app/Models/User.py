"""
User Model
"""
from vendor.Illuminate.Database.Model import Model
import bcrypt
from datetime import datetime


class User(Model):
    """User model for authentication"""
    
    table = "users"
    
    fillable = [
        "name",
        "email",
        "password",
        "avatar",
        "role",
        "is_active"
    ]
    
    hidden = ["password"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        # Convert password to bytes and hash with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')  # Return as string for database storage
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not hasattr(self, 'password') or not self.password:
            return False
        # Convert password and hash to bytes for comparison
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_user(self) -> bool:
        """Check if user is regular user"""
        return self.role == 'user'
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        data = super().to_dict()
        # Remove password from output
        data.pop('password', None)
        return data
    
    @classmethod
    async def find_by_email(cls, email: str):
        """Find user by email"""
        return await cls.where('email', email).first()
    
    @classmethod
    async def create_user(cls, name: str, email: str, password: str, role: str = 'user'):
        """Create a new user with hashed password"""
        hashed_password = cls.hash_password(password)
        return await cls.create({
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': role,
            'is_active': True
        })
    
    async def posts(self):
        """Get all posts by this user"""
        from app.Models.Post import Post
        return await Post.where('user_id', self.id).get()
