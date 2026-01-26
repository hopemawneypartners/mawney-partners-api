"""
Encryption utilities for sensitive data
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from config import settings

# Initialize encryption key
_encryption_key = None
_fernet = None

def get_encryption_key() -> bytes:
    """
    Get or generate encryption key
    
    Returns:
        Encryption key as bytes
    """
    global _encryption_key
    
    if _encryption_key is None:
        key_str = settings.ENCRYPTION_KEY
        
        # If key is a hex string, convert to bytes
        if len(key_str) == 64:  # 32 bytes = 64 hex chars
            try:
                _encryption_key = bytes.fromhex(key_str)
            except ValueError:
                # If not valid hex, use as-is and derive key
                _encryption_key = derive_key_from_string(key_str)
        else:
            # Derive key from string
            _encryption_key = derive_key_from_string(key_str)
        
        # Ensure key is 32 bytes for Fernet
        if len(_encryption_key) != 32:
            _encryption_key = _encryption_key[:32] if len(_encryption_key) > 32 else _encryption_key.ljust(32, b'0')
    
    return _encryption_key

def derive_key_from_string(password: str, salt: bytes = None) -> bytes:
    """
    Derive encryption key from password string
    
    Args:
        password: Password string
        salt: Salt bytes (generates new if None)
        
    Returns:
        Derived key as bytes
    """
    if salt is None:
        salt = b'mawney_partners_salt_2024'  # Fixed salt for consistency
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def get_fernet() -> Fernet:
    """
    Get Fernet encryption instance
    
    Returns:
        Fernet instance
    """
    global _fernet
    
    if _fernet is None:
        key = get_encryption_key()
        # Fernet requires base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(key)
        _fernet = Fernet(fernet_key)
    
    return _fernet

def encrypt_field(data: str) -> str:
    """
    Encrypt a string field
    
    Args:
        data: Plain text string to encrypt
        
    Returns:
        Encrypted string (base64 encoded)
    """
    if not data:
        return ""
    
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Error encrypting field: {e}")
        return data  # Return original if encryption fails

def decrypt_field(encrypted_data: str) -> str:
    """
    Decrypt an encrypted field
    
    Args:
        encrypted_data: Encrypted string (base64 encoded)
        
    Returns:
        Decrypted plain text string
    """
    if not encrypted_data:
        return ""
    
    try:
        fernet = get_fernet()
        # Decode from base64
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Error decrypting field: {e}")
        return encrypted_data  # Return original if decryption fails

def generate_encryption_key() -> str:
    """
    Generate a new encryption key
    
    Returns:
        Base64-encoded encryption key string
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')

def encrypt_dict_fields(data: dict, fields_to_encrypt: list) -> dict:
    """
    Encrypt specific fields in a dictionary
    
    Args:
        data: Dictionary to encrypt fields in
        fields_to_encrypt: List of field names to encrypt
        
    Returns:
        Dictionary with encrypted fields
    """
    encrypted_data = data.copy()
    
    for field in fields_to_encrypt:
        if field in encrypted_data and encrypted_data[field]:
            encrypted_data[field] = encrypt_field(str(encrypted_data[field]))
    
    return encrypted_data

def decrypt_dict_fields(data: dict, fields_to_decrypt: list) -> dict:
    """
    Decrypt specific fields in a dictionary
    
    Args:
        data: Dictionary to decrypt fields in
        fields_to_decrypt: List of field names to decrypt
        
    Returns:
        Dictionary with decrypted fields
    """
    decrypted_data = data.copy()
    
    for field in fields_to_decrypt:
        if field in decrypted_data and decrypted_data[field]:
            decrypted_data[field] = decrypt_field(str(decrypted_data[field]))
    
    return decrypted_data

# Sensitive fields that should be encrypted
SENSITIVE_FIELDS = {
    'compensation': [
        'baseSalary',
        'baseSalaryCurrency',
        'bonus',
        'bonusCurrency',
        'equity',
        'carry',
        'deferredComp',
    ],
    'call_notes': [
        'transcript',
        'summary',
        'notes',
    ],
    'user_profile': [
        'email',
        'phone',
        'address',
    ],
    'device_tokens': [
        'device_token',
    ],
}
