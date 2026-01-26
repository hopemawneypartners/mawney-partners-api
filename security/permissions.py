"""
Permission and access control utilities
"""
from functools import wraps
from flask import request, jsonify
from typing import List, Callable
from .auth import get_current_user, require_auth

# Permission definitions
PERMISSIONS = {
    'admin': ['*'],  # All permissions
    'user': [
        'read:own_compensation',
        'write:own_compensation',
        'read:own_call_notes',
        'write:own_call_notes',
        'read:own_todos',
        'write:own_todos',
        'read:own_chats',
        'write:own_chats',
        'read:own_industry_moves',
        'write:own_industry_moves',
        'read:own_profile',
        'write:own_profile',
    ],
    'read-only': [
        'read:own_compensation',
        'read:own_call_notes',
        'read:own_todos',
        'read:own_chats',
        'read:own_industry_moves',
        'read:own_profile',
    ]
}

def get_user_permissions(user: dict) -> List[str]:
    """
    Get permissions for a user based on their roles
    
    Args:
        user: User dictionary with roles
        
    Returns:
        List of permissions
    """
    permissions = set()
    roles = user.get('roles', [])
    
    for role in roles:
        if role in PERMISSIONS:
            role_perms = PERMISSIONS[role]
            if '*' in role_perms:
                return ['*']  # Admin has all permissions
            permissions.update(role_perms)
    
    return list(permissions)

def has_permission(user: dict, permission: str) -> bool:
    """
    Check if user has a specific permission
    
    Args:
        user: User dictionary
        permission: Permission to check (e.g., 'read:own_compensation')
        
    Returns:
        True if user has permission
    """
    user_perms = get_user_permissions(user)
    
    # Admin has all permissions
    if '*' in user_perms:
        return True
    
    # Check exact permission
    if permission in user_perms:
        return True
    
    # Check wildcard permissions (e.g., 'read:*' matches 'read:own_compensation')
    for perm in user_perms:
        if perm.endswith(':*'):
            prefix = perm[:-2]
            if permission.startswith(prefix + ':'):
                return True
    
    return False

def require_permission(permission: str):
    """
    Decorator to require a specific permission
    
    Usage:
        @app.route('/api/compensations')
        @require_auth
        @require_permission('read:own_compensation')
        def get_compensations():
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            if not has_permission(user, permission):
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_ownership(data_owner_field: str = 'email', request_param: str = 'email'):
    """
    Decorator to require user owns the data they're accessing
    
    Usage:
        @app.route('/api/compensations')
        @require_auth
        @require_ownership('email', 'email')
        def get_compensations():
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            # Admin can access all data
            if '*' in get_user_permissions(user):
                return f(*args, **kwargs)
            
            # Get owner identifier from request
            owner_identifier = None
            
            # Try to get from request args (GET)
            if request.method == 'GET':
                owner_identifier = request.args.get(request_param)
            
            # Try to get from JSON body (POST/PUT)
            if not owner_identifier and request.is_json:
                data = request.get_json()
                owner_identifier = data.get(request_param)
            
            # Try to get from form data
            if not owner_identifier:
                owner_identifier = request.form.get(request_param)
            
            # Verify ownership
            user_email = user.get('email')
            user_id = user.get('user_id')
            
            # Check if user owns the data
            if owner_identifier and owner_identifier not in [user_email, user_id]:
                return jsonify({
                    'success': False,
                    'error': 'Access denied: You can only access your own data'
                }), 403
            
            # If no owner identifier provided, use current user's
            if not owner_identifier:
                # Set owner to current user
                if request.method == 'GET':
                    request.args = request.args.copy()
                    request.args[request_param] = user_email
                elif request.is_json:
                    data = request.get_json() or {}
                    data[request_param] = user_email
                    request.json = data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def verify_data_ownership(data: dict, user: dict, owner_field: str = 'email') -> bool:
    """
    Verify that user owns the data
    
    Args:
        data: Data dictionary
        user: User dictionary
        owner_field: Field name that contains owner identifier
        
    Returns:
        True if user owns the data
    """
    # Admin can access all data
    if '*' in get_user_permissions(user):
        return True
    
    user_email = user.get('email')
    user_id = user.get('user_id')
    data_owner = data.get(owner_field)
    
    return data_owner in [user_email, user_id]
