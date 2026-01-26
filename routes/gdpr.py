"""
GDPR compliance endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from database.models import User, Compensation, CallNote, SessionLocal
from security.auth import get_current_user
from security.audit import get_audit_logs, log_data_access, log_data_modification
from security.encryption import decrypt_dict_fields, SENSITIVE_FIELDS
from security.rate_limit import rate_limit_data_export
import json

gdpr_bp = Blueprint('gdpr', __name__, url_prefix='/api/user')

@gdpr_bp.route('/data-export', methods=['GET'])
@jwt_required()
@rate_limit_data_export()
def export_user_data():
    """Export all user data (GDPR Right to Access)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_email = user.get('email')
        user_id = user.get('user_id')
        
        # Log data access
        log_data_access(user_id, user_email, 'data_export', 1, '/api/user/data-export')
        
        db = SessionLocal()
        try:
            # Get user profile
            db_user = db.query(User).filter(User.id == user_id).first()
            user_data = {
                'id': db_user.id if db_user else user_id,
                'email': db_user.email if db_user else user_email,
                'roles': db_user.roles if db_user else [],
                'mfa_enabled': db_user.mfa_enabled if db_user else False,
                'created_at': db_user.created_at.isoformat() if db_user and db_user.created_at else None,
                'last_login': db_user.last_login.isoformat() if db_user and db_user.last_login else None,
            }
            
            # Get compensations
            compensations = db.query(Compensation).filter(
                Compensation.user_email == user_email,
                Compensation.is_deleted == False
            ).all()
            
            compensation_data = []
            for comp in compensations:
                comp_dict = {
                    'id': comp.id,
                    'base_salary': comp.base_salary,
                    'base_salary_currency': comp.base_salary_currency,
                    'bonus': comp.bonus,
                    'bonus_currency': comp.bonus_currency,
                    'equity': comp.equity,
                    'country': comp.country,
                    'role': comp.role,
                    'company': comp.company,
                    'created_at': comp.created_at.isoformat() if comp.created_at else None,
                    'updated_at': comp.updated_at.isoformat() if comp.updated_at else None,
                }
                # Decrypt sensitive fields
                comp_dict = decrypt_dict_fields(comp_dict, SENSITIVE_FIELDS.get('compensation', []))
                compensation_data.append(comp_dict)
            
            # Get call notes
            call_notes = db.query(CallNote).filter(
                CallNote.user_email == user_email,
                CallNote.is_deleted == False
            ).all()
            
            call_notes_data = []
            for note in call_notes:
                note_dict = {
                    'id': note.id,
                    'title': note.title,
                    'transcript': note.transcript,
                    'summary': note.summary,
                    'notes': note.notes,
                    'date': note.date.isoformat() if note.date else None,
                    'participants': note.participants,
                    'created_at': note.created_at.isoformat() if note.created_at else None,
                    'updated_at': note.updated_at.isoformat() if note.updated_at else None,
                }
                # Decrypt sensitive fields
                note_dict = decrypt_dict_fields(note_dict, SENSITIVE_FIELDS.get('call_notes', []))
                call_notes_data.append(note_dict)
            
            # Get audit logs for user
            audit_logs = get_audit_logs(user_id=user_id, limit=1000)
            
            # Compile all data
            export_data = {
                'export_date': datetime.utcnow().isoformat(),
                'user': user_data,
                'compensations': compensation_data,
                'call_notes': call_notes_data,
                'audit_logs': audit_logs,
                'metadata': {
                    'total_compensations': len(compensation_data),
                    'total_call_notes': len(call_notes_data),
                    'total_audit_logs': len(audit_logs),
                }
            }
            
            return jsonify({
                'success': True,
                'data': export_data,
                'format': 'json',
                'message': 'Data export successful'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in data export: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Data export failed'
        }), 500

@gdpr_bp.route('/data-delete', methods=['DELETE'])
@jwt_required()
def delete_user_data():
    """Delete all user data (GDPR Right to Deletion) - Soft delete with retention period"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.get_json() or {}
        confirm = data.get('confirm', False)
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'Please confirm deletion by setting "confirm": true'
            }), 400
        
        user_email = user.get('email')
        user_id = user.get('user_id')
        
        db = SessionLocal()
        try:
            # Soft delete user
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                db_user.is_deleted = True
                db_user.is_active = False
            
            # Soft delete compensations
            compensations = db.query(Compensation).filter(
                Compensation.user_email == user_email,
                Compensation.is_deleted == False
            ).all()
            for comp in compensations:
                comp.is_deleted = True
                log_data_modification(user_id, user_email, 'compensation', 'delete', comp.id)
            
            # Soft delete call notes
            call_notes = db.query(CallNote).filter(
                CallNote.user_email == user_email,
                CallNote.is_deleted == False
            ).all()
            for note in call_notes:
                note.is_deleted = True
                log_data_modification(user_id, user_email, 'call_notes', 'delete', note.id)
            
            db.commit()
            
            # Log deletion
            log_data_modification(user_id, user_email, 'user_data', 'delete', user_id)
            
            return jsonify({
                'success': True,
                'message': 'Data deletion initiated. Data will be permanently deleted after retention period.',
                'retention_days': 30,
                'note': 'Your data has been soft-deleted and will be permanently removed after 30 days.'
            }), 200
            
        except Exception as e:
            db.rollback()
            print(f"Error in data deletion: {e}")
            return jsonify({
                'success': False,
                'error': 'Data deletion failed'
            }), 500
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in delete_user_data: {e}")
        return jsonify({
            'success': False,
            'error': 'Data deletion failed'
        }), 500

@gdpr_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_user_audit_logs():
    """Get user's audit logs"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = user.get('user_id')
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        event_type = request.args.get('event_type')
        limit = int(request.args.get('limit', 100))
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Get audit logs
        logs = get_audit_logs(
            start_date=start,
            end_date=end,
            user_id=user_id,
            event_type=event_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        }), 200
        
    except Exception as e:
        print(f"Error getting audit logs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audit logs'
        }), 500
