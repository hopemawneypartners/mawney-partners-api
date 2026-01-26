"""
Rate limiting configuration
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from flask import Flask
from config import settings

# Initialize rate limiter
limiter = None

def setup_rate_limiting(app: Flask):
    """
    Set up rate limiting for Flask app
    
    Args:
        app: Flask application instance
    """
    global limiter
    
    # Redis connection for rate limiting
    redis_url = None
    redis_config = {}
    
    try:
        if settings.REDIS_URL:
            redis_url = settings.REDIS_URL
        elif settings.REDIS_PASSWORD:
            redis_config = {
                'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT,
                'db': settings.REDIS_DB,
                'password': settings.REDIS_PASSWORD,
            }
        else:
            redis_config = {
                'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT,
                'db': settings.REDIS_DB,
            }
        
        # Test Redis connection
        if redis_url:
            test_client = redis.from_url(redis_url)
        else:
            test_client = redis.Redis(**redis_config)
        test_client.ping()
        redis_available = True
    except Exception as e:
        print(f"⚠️ Redis not available for rate limiting: {e}")
        print("   Falling back to in-memory rate limiting")
        redis_available = False
        redis_url = None
        redis_config = {}
    
    # Initialize limiter
    if redis_available:
        if redis_url:
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                storage_uri=redis_url,
                default_limits=[
                    f"{settings.RATE_LIMIT_PER_MINUTE} per minute",
                    f"{settings.RATE_LIMIT_PER_HOUR} per hour"
                ] if settings.RATE_LIMIT_ENABLED else None,
                strategy="fixed-window"
            )
        else:
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                storage_uri=f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}",
                default_limits=[
                    f"{settings.RATE_LIMIT_PER_MINUTE} per minute",
                    f"{settings.RATE_LIMIT_PER_HOUR} per hour"
                ] if settings.RATE_LIMIT_ENABLED else None,
                strategy="fixed-window"
            )
    else:
        # Fallback to in-memory (not recommended for production)
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[
                f"{settings.RATE_LIMIT_PER_MINUTE} per minute",
                f"{settings.RATE_LIMIT_PER_HOUR} per hour"
            ] if settings.RATE_LIMIT_ENABLED else None,
            strategy="fixed-window"
        )
    
    # Configure rate limits
    if settings.RATE_LIMIT_ENABLED:
        # Default limits are already set in Limiter initialization above
        print(f"✅ Rate limiting enabled: {settings.RATE_LIMIT_PER_MINUTE}/min, {settings.RATE_LIMIT_PER_HOUR}/hour")
    else:
        print("⚠️ Rate limiting disabled")
    
    return limiter

def get_rate_limiter():
    """Get rate limiter instance"""
    return limiter

# Rate limit decorators for specific endpoints
def rate_limit_auth():
    """Rate limit for authentication endpoints"""
    if limiter is None:
        # Return a no-op decorator if limiter not initialized yet
        def noop_decorator(f):
            return f
        return noop_decorator
    return limiter.limit(f"{settings.RATE_LIMIT_AUTH_ATTEMPTS} per minute")

def rate_limit_data_export():
    """Rate limit for data export endpoints"""
    if limiter is None:
        def noop_decorator(f):
            return f
        return noop_decorator
    return limiter.limit("1 per hour")

def rate_limit_file_upload():
    """Rate limit for file upload endpoints"""
    if limiter is None:
        def noop_decorator(f):
            return f
        return noop_decorator
    return limiter.limit("10 per minute")
