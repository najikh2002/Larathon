"""
JWT Authentication Helper
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict


class JWT:
    """JWT token generator and validator"""
    
    @staticmethod
    def get_secret() -> str:
        """Get JWT secret from environment"""
        secret = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
        if secret == 'your-secret-key-change-this':
            import warnings
            warnings.warn("Using default SECRET_KEY! Set SECRET_KEY in .env for production!")
        return secret
    
    @staticmethod
    def generate(user_id: int, email: str, role: str = 'user', expires_in: int = 24) -> str:
        """
        Generate JWT token
        
        Args:
            user_id: User ID
            email: User email
            role: User role (default: 'user')
            expires_in: Token expiration in hours (default: 24)
        
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=expires_in),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT.get_secret(), algorithm='HS256')
        return token
    
    @staticmethod
    def decode(token: str) -> Optional[Dict]:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload dict or None if invalid
        """
        try:
            payload = jwt.decode(token, JWT.get_secret(), algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    @staticmethod
    def verify(token: str) -> bool:
        """
        Verify if token is valid
        
        Args:
            token: JWT token string
        
        Returns:
            True if valid, False otherwise
        """
        return JWT.decode(token) is not None
    
    @staticmethod
    def extract_from_header(auth_header: Optional[str]) -> Optional[str]:
        """
        Extract token from Authorization header
        
        Args:
            auth_header: Authorization header value (e.g., "Bearer token123")
        
        Returns:
            Token string or None
        """
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
