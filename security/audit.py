"""
Audit logging for GDPR compliance and security monitoring
"""
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request
import json
import os

# Audit log storage (in production, use database)
AUDIT_LOG_DIR = "audit_logs"

def ensure_audit_log_dir():
    """Ensure audit log directory exists"""
    if not os.path.exists(AUDIT_LOG_DIR):
        os.makedirs(AUDIT_LOG_DIR)

def sanitize_user_agent(user_agent: Optional[str]) -> Optional[str]:
    """
    Sanitize user agent string to remove development tool references
    """
    if not user_agent:
        return None
    
    # List of development tools to remove/replace
    dev_tools = ['cursor', 'vscode', 'postman', 'insomnia', 'httpie', 'curl']
    
    user_agent_lower = user_agent.lower()
    for tool in dev_tools:
        if tool in user_agent_lower:
            # Replace with generic identifier
            return "Development Tool"
    
    # If it's a known browser or app, keep it but anonymize version details
    if any(browser in user_agent_lower for browser in ['mozilla', 'chrome', 'safari', 'edge', 'firefox']):
        # Keep browser name but simplify
        if 'mozilla' in user_agent_lower:
            return "Mozilla/5.0 (Browser)"
        elif 'chrome' in user_agent_lower:
            return "Chrome Browser"
        elif 'safari' in user_agent_lower:
            return "Safari Browser"
        elif 'edge' in user_agent_lower:
            return "Edge Browser"
        elif 'firefox' in user_agent_lower:
            return "Firefox Browser"
    
    # For unknown user agents, return generic
    return "Unknown Client"

def log_event(
    event_type: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log an audit event
    
    Args:
        event_type: Type of event (e.g., 'data_access', 'authentication', 'data_modification')
        user_id: User identifier
        email: User email
        endpoint: API endpoint
        method: HTTP method
        status: Event status (success, failure, error)
        details: Additional event details
        ip_address: Client IP address
        user_agent: Client user agent
    """
    ensure_audit_log_dir()
    
    # Get request info if not provided
    if not ip_address:
        ip_address = request.remote_addr if request else None
    if not user_agent:
        user_agent = request.headers.get('User-Agent') if request else None
    if not endpoint:
        endpoint = request.path if request else None
    if not method:
        method = request.method if request else None
    
    # Sanitize user agent to remove development tool references
    user_agent = sanitize_user_agent(user_agent)
    
    # Create audit log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "email": email,
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "details": details or {}
    }
    
    # Write to log file (daily rotation)
    log_date = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = os.path.join(AUDIT_LOG_DIR, f"audit_{log_date}.jsonl")
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Error writing audit log: {e}")
    
    # Also print to console for development
    if os.getenv("DEBUG", "False").lower() == "true":
        print(f"📋 Audit: {event_type} - {email or user_id} - {endpoint} - {status}")

def log_data_access(
    user_id: str,
    email: str,
    data_type: str,
    record_count: int = 1,
    endpoint: Optional[str] = None
):
    """
    Log data access event
    
    Args:
        user_id: User identifier
        email: User email
        data_type: Type of data accessed (e.g., 'compensation', 'call_notes')
        record_count: Number of records accessed
        endpoint: API endpoint
    """
    log_event(
        event_type="data_access",
        user_id=user_id,
        email=email,
        endpoint=endpoint,
        details={
            "data_type": data_type,
            "record_count": record_count
        }
    )

def log_data_modification(
    user_id: str,
    email: str,
    data_type: str,
    action: str,  # 'create', 'update', 'delete'
    record_id: Optional[str] = None,
    endpoint: Optional[str] = None
):
    """
    Log data modification event
    
    Args:
        user_id: User identifier
        email: User email
        data_type: Type of data modified
        action: Action performed
        record_id: Record identifier
        endpoint: API endpoint
    """
    log_event(
        event_type="data_modification",
        user_id=user_id,
        email=email,
        endpoint=endpoint,
        details={
            "data_type": data_type,
            "action": action,
            "record_id": record_id
        }
    )

def log_authentication(
    email: str,
    success: bool,
    method: str = "password",  # 'password', 'token', 'mfa'
    failure_reason: Optional[str] = None
):
    """
    Log authentication event
    
    Args:
        email: User email
        success: Whether authentication was successful
        method: Authentication method
        failure_reason: Reason for failure (if unsuccessful)
    """
    log_event(
        event_type="authentication",
        email=email,
        status="success" if success else "failure",
        details={
            "method": method,
            "failure_reason": failure_reason
        }
    )

def log_security_event(
    event_type: str,
    severity: str,  # 'low', 'medium', 'high', 'critical'
    description: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log security event
    
    Args:
        event_type: Type of security event
        severity: Event severity
        description: Event description
        user_id: User identifier (if applicable)
        email: User email (if applicable)
        details: Additional details
    """
    log_event(
        event_type=f"security_{event_type}",
        user_id=user_id,
        email=email,
        status=severity,
        details={
            "description": description,
            "severity": severity,
            **(details or {})
        }
    )

def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 1000
) -> list:
    """
    Retrieve audit logs (for admin/GDPR purposes)
    
    Args:
        start_date: Start date for log retrieval
        end_date: End date for log retrieval
        user_id: Filter by user ID
        event_type: Filter by event type
        limit: Maximum number of logs to return
        
    Returns:
        List of audit log entries
    """
    ensure_audit_log_dir()
    
    logs = []
    
    # Determine date range
    if not start_date:
        start_date = datetime.utcnow().replace(day=1)  # Start of current month
    if not end_date:
        end_date = datetime.utcnow()
    
    # Iterate through date range
    current_date = start_date
    while current_date <= end_date:
        log_date = current_date.strftime("%Y-%m-%d")
        log_file = os.path.join(AUDIT_LOG_DIR, f"audit_{log_date}.jsonl")
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        log_entry = json.loads(line)
                        
                        # Apply filters
                        if user_id and log_entry.get('user_id') != user_id:
                            continue
                        if event_type and log_entry.get('event_type') != event_type:
                            continue
                        
                        logs.append(log_entry)
                        
                        if len(logs) >= limit:
                            break
            except Exception as e:
                print(f"Error reading audit log {log_file}: {e}")
        
        if len(logs) >= limit:
            break
        
        # Move to next day
        from datetime import timedelta
        current_date += timedelta(days=1)
    
    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return logs[:limit]
