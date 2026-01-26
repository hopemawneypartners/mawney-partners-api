"""
Authentication and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token as jwt_create_access_token,
    create_refresh_token as jwt_create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    verify_jwt_in_request
)
import jwt
import hashlib
import redis
from config import settings

# Redis connection for token blacklist (optional, falls back to in-memory if not available)
try:
    if settings.REDIS_URL:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    elif settings.REDIS_PASSWORD:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    else:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    redis_client.ping()
    redis_available = True
except Exception:
    # Fallback to in-memory blacklist if Redis not available
    redis_available = False
    token_blacklist = set()

def create_access_token(user_id: str, email: str, roles: list = None, permissions: list = None) -> str:
    """
    Create a JWT access token
    
    Args:
        user_id: User identifier
        email: User email
        roles: List of user roles
        permissions: List of user permissions
        
    Returns:
        JWT access token string
    """
    if roles is None:
        roles = ["user"]
    if permissions is None:
        permissions = get_default_permissions(roles)
    
    additional_claims = {
        "email": email,
        "roles": roles,
        "permissions": permissions,
        "type": "access"
    }
    
    expires = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    token = jwt_create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=expires
    )
    
    return token

def create_refresh_token(user_id: str, email: str) -> str:
    """
    Create a JWT refresh token
    
    Args:
        user_id: User identifier
        email: User email
        
    Returns:
        JWT refresh token string
    """
    additional_claims = {
        "email": email,
        "type": "refresh"
    }
    
    expires = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
    token = jwt_create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=expires
    )
    
    # Store refresh token hash for rotation
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    store_refresh_token(user_id, token_hash, expires.total_seconds())
    
    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            return None
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def blacklist_token(token: str, expires_in: int = None):
    """
    Add token to blacklist
    
    Args:
        token: JWT token to blacklist
        expires_in: Expiration time in seconds (defaults to token expiration)
    """
    try:
        # Decode token to get expiration
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False}
        )
        
        exp = payload.get("exp", 0)
        current_time = datetime.utcnow().timestamp()
        ttl = int(exp - current_time) if exp > current_time else 3600
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if redis_available:
            redis_client.setex(f"blacklist:{token_hash}", ttl, "1")
        else:
            token_blacklist.add(token_hash)
    except Exception as e:
        print(f"Error blacklisting token: {e}")

def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted
    
    Args:
        token: JWT token to check
        
    Returns:
        True if token is blacklisted
    """
    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if redis_available:
            return redis_client.exists(f"blacklist:{token_hash}") > 0
        else:
            return token_hash in token_blacklist
    except Exception:
        return False

def store_refresh_token(user_id: str, token_hash: str, expires_in: float):
    """
    Store refresh token hash for rotation
    
    Args:
        user_id: User identifier
        token_hash: Hashed refresh token
        expires_in: Expiration time in seconds
    """
    try:
        if redis_available:
            redis_client.setex(f"refresh_token:{user_id}:{token_hash}", int(expires_in), "1")
        # In-memory fallback not needed for refresh tokens (they're validated via JWT)
    except Exception as e:
        print(f"Error storing refresh token: {e}")

def revoke_refresh_token(user_id: str, token: str):
    """
    Revoke a refresh token (for logout or security)
    
    Args:
        user_id: User identifier
        token: Refresh token to revoke
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    blacklist_token(token)
    
    try:
        if redis_available:
            # Remove from refresh token store
            redis_client.delete(f"refresh_token:{user_id}:{token_hash}")
    except Exception as e:
        print(f"Error revoking refresh token: {e}")

def get_current_user():
    """
    Get current authenticated user from JWT token
    
    Returns:
        Dictionary with user information
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        return {
            "user_id": user_id,
            "email": claims.get("email"),
            "roles": claims.get("roles", []),
            "permissions": claims.get("permissions", [])
        }
    except Exception:
        return None

def get_default_permissions(roles: list) -> list:
    """
    Get default permissions for roles
    
    Args:
        roles: List of user roles
        
    Returns:
        List of permissions
    """
    permissions = []
    
    if "admin" in roles:
        permissions = ["*"]  # All permissions
    elif "user" in roles:
        permissions = [
            "read:own_compensation",
            "write:own_compensation",
            "read:own_call_notes",
            "write:own_call_notes",
            "read:own_todos",
            "write:own_todos",
            "read:own_chats",
            "write:own_chats",
            "read:own_industry_moves",
            "write:own_industry_moves",
        ]
    elif "read-only" in roles:
        permissions = [
            "read:own_compensation",
            "read:own_call_notes",
            "read:own_todos",
            "read:own_chats",
            "read:own_industry_moves",
        ]
    
    return permissions

def require_auth(f):
    """
    Decorator to require authentication
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user = get_current_user()
            return jsonify({"user": user})
    """
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function
