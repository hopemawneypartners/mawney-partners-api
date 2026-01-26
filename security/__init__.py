"""
Security module for Mawney Partners API
"""
from .auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    require_auth,
    blacklist_token,
    revoke_refresh_token
)
from .encryption import (
    encrypt_field,
    decrypt_field,
    generate_encryption_key,
    encrypt_dict_fields,
    decrypt_dict_fields,
    SENSITIVE_FIELDS
)
from .permissions import (
    require_permission,
    require_ownership,
    get_user_permissions,
    has_permission,
    PERMISSIONS
)
from .rate_limit import (
    setup_rate_limiting,
    get_rate_limiter,
    rate_limit_auth,
    rate_limit_data_export,
    rate_limit_file_upload
)
from .audit import (
    log_event,
    log_data_access,
    log_data_modification,
    log_authentication,
    log_security_event,
    get_audit_logs
)

__all__ = [
    # Authentication
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'get_current_user',
    'require_auth',
    'blacklist_token',
    'revoke_refresh_token',
    # Encryption
    'encrypt_field',
    'decrypt_field',
    'generate_encryption_key',
    'encrypt_dict_fields',
    'decrypt_dict_fields',
    'SENSITIVE_FIELDS',
    # Permissions
    'require_permission',
    'require_ownership',
    'get_user_permissions',
    'has_permission',
    'PERMISSIONS',
    # Rate Limiting
    'setup_rate_limiting',
    'get_rate_limiter',
    'rate_limit_auth',
    'rate_limit_data_export',
    'rate_limit_file_upload',
    # Audit Logging
    'log_event',
    'log_data_access',
    'log_data_modification',
    'log_authentication',
    'log_security_event',
    'get_audit_logs',
]
