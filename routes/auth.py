"""
Authentication endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import bcrypt
import pyotp
import qrcode
import io
import base64
from database.models import User, SessionLocal
from security.auth import (
    create_access_token,
    create_refresh_token,
    blacklist_token,
    revoke_refresh_token,
    get_current_user
)
from security.audit import log_authentication, log_security_event
from security.rate_limit import rate_limit_auth
from security.permissions import get_user_permissions
from config import settings

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

@auth_bp.route('/login', methods=['POST'])
@rate_limit_auth()
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            log_authentication(email, False, 'password', 'Missing email or password')
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        # Get user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
            
            if not user:
                log_authentication(email, False, 'password', 'User not found')
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401
            
            # Verify password
            if not verify_password(password, user.password_hash):
                log_authentication(email, False, 'password', 'Invalid password')
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401
            
            # Check if user is active
            if not user.is_active:
                log_authentication(email, False, 'password', 'Account inactive')
                return jsonify({
                    'success': False,
                    'error': 'Account is inactive'
                }), 403
            
            # Check if MFA is required
            mfa_required = user.mfa_enabled
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Log successful authentication
            log_authentication(email, True, 'password')
            
            # Generate tokens
            access_token = create_access_token(
                user_id=user.id,
                email=user.email,
                roles=user.roles or ['user'],
                permissions=get_user_permissions({'roles': user.roles or ['user']})
            )
            refresh_token = create_refresh_token(user.id, user.email)
            
            response_data = {
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'roles': user.roles or ['user'],
                    'mfa_enabled': mfa_required
                }
            }
            
            # If MFA is enabled, require MFA verification before returning tokens
            if mfa_required:
                # Don't return tokens yet, require MFA
                response_data['mfa_required'] = True
                response_data['access_token'] = None
                response_data['refresh_token'] = None
                # Store temporary token for MFA verification (in production, use session)
                # For now, we'll require MFA on every login if enabled
            
            return jsonify(response_data), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again.'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
            
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'User not found or inactive'
                }), 401
            
            # Revoke old refresh token (token rotation)
            old_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            revoke_refresh_token(user_id, old_token)
            
            # Generate new tokens
            access_token = create_access_token(
                user_id=user.id,
                email=user.email,
                roles=user.roles or ['user'],
                permissions=get_user_permissions({'roles': user.roles or ['user']})
            )
            new_refresh_token = create_refresh_token(user.id, user.email)
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'refresh_token': new_refresh_token
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in refresh: {e}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout and revoke tokens"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get token from request
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Blacklist access token
        blacklist_token(token)
        
        # Revoke refresh token if provided
        refresh_token = request.get_json().get('refresh_token') if request.is_json else None
        if refresh_token:
            revoke_refresh_token(user_id, refresh_token)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@auth_bp.route('/register', methods=['POST'])
@rate_limit_auth()
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }), 400
        
        # Check if user already exists
        db = SessionLocal()
        try:
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'User already exists'
                }), 409
            
            # Create new user
            import uuid
            user_id = str(uuid.uuid4())
            password_hash = hash_password(password)
            
            new_user = User(
                id=user_id,
                email=email,
                password_hash=password_hash,
                roles=['user'],
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            
            log_authentication(email, True, 'registration')
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user_id,
                    'email': email
                }
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in register: {e}")
        import traceback
        traceback.print_exc()
        # Return more specific error message for debugging
        error_msg = str(e)
        if 'no such table' in error_msg.lower() or 'operationalerror' in error_msg.lower():
            error_msg = 'Database not initialized. Please contact support.'
        return jsonify({
            'success': False,
            'error': f'Registration failed: {error_msg}'
        }), 500

@auth_bp.route('/mfa/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    """Set up MFA (TOTP) for user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user['user_id']).first()
            if not db_user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Generate TOTP secret
            totp_secret = pyotp.random_base32()
            
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=db_user.email,
                issuer_name=settings.MFA_ISSUER_NAME
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Generate backup codes
            backup_codes = [pyotp.random_base32()[:8].upper() for _ in range(10)]
            
            # Store secret and backup codes (but don't enable MFA yet)
            db_user.mfa_secret = totp_secret
            db_user.backup_codes = backup_codes
            db.commit()
            
            return jsonify({
                'success': True,
                'qr_code': f'data:image/png;base64,{qr_code_base64}',
                'secret': totp_secret,  # For manual entry
                'backup_codes': backup_codes,
                'message': 'Scan QR code with authenticator app, then verify with /api/auth/mfa/verify'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in setup_mfa: {e}")
        return jsonify({
            'success': False,
            'error': 'MFA setup failed'
        }), 500

@auth_bp.route('/mfa/verify', methods=['POST'])
@jwt_required()
def verify_mfa():
    """Verify MFA code and enable MFA"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'MFA code required'
            }), 400
        
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user['user_id']).first()
            if not db_user or not db_user.mfa_secret:
                return jsonify({
                    'success': False,
                    'error': 'MFA not set up. Please set up MFA first.'
                }), 400
            
            # Verify TOTP code
            totp = pyotp.TOTP(db_user.mfa_secret)
            if not totp.verify(code, valid_window=1):
                log_security_event('mfa_verification_failed', 'medium', 
                                  'Failed MFA verification attempt', 
                                  user_id=user['user_id'], email=user['email'])
                return jsonify({
                    'success': False,
                    'error': 'Invalid MFA code'
                }), 401
            
            # Enable MFA
            db_user.mfa_enabled = True
            db.commit()
            
            log_security_event('mfa_enabled', 'low', 
                              'MFA enabled for user', 
                              user_id=user['user_id'], email=user['email'])
            
            return jsonify({
                'success': True,
                'message': 'MFA enabled successfully'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in verify_mfa: {e}")
        return jsonify({
            'success': False,
            'error': 'MFA verification failed'
        }), 500

@auth_bp.route('/mfa/disable', methods=['POST'])
@jwt_required()
def disable_mfa():
    """Disable MFA for user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password required to disable MFA'
            }), 400
        
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user['user_id']).first()
            if not db_user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Verify password
            if not verify_password(password, db_user.password_hash):
                return jsonify({
                    'success': False,
                    'error': 'Invalid password'
                }), 401
            
            # Disable MFA
            db_user.mfa_enabled = False
            db_user.mfa_secret = None
            db_user.backup_codes = None
            db.commit()
            
            log_security_event('mfa_disabled', 'medium', 
                              'MFA disabled for user', 
                              user_id=user['user_id'], email=user['email'])
            
            return jsonify({
                'success': True,
                'message': 'MFA disabled successfully'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in disable_mfa: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to disable MFA'
        }), 500
