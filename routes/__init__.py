"""
API Routes
"""
from .auth import auth_bp
from .gdpr import gdpr_bp

__all__ = ['auth_bp', 'gdpr_bp']
