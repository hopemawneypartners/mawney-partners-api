"""
Security Monitoring Bot
Monitors API logs for security threats and anomalies
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import re

class SecurityMonitor:
    """Real-time security monitoring and threat detection"""
    
    def __init__(self, audit_log_dir: str = "audit_logs", alert_email: Optional[str] = None):
        self.audit_log_dir = audit_log_dir
        self.alert_email = alert_email
        self.threat_patterns = self._load_threat_patterns()
        self.anomaly_thresholds = self._load_anomaly_thresholds()
        self.user_baselines = {}  # Track normal behavior per user
        
    def _load_threat_patterns(self) -> Dict:
        """Load threat detection patterns"""
        return {
            'sql_injection': [
                r"('|(\\')|(;)|(--)|(/\*)|(\*/)|(\+)|(\|)|(\&)|(\%)|(\$)|(\#)|(\@)|(\!)",
                r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
                r"(\bor\b.*=.*=|\band\b.*=.*=)",
            ],
            'xss': [
                r"<script",
                r"javascript:",
                r"onerror\s*=",
                r"onload\s*=",
                r"<iframe",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"c:\\windows",
            ],
            'command_injection': [
                r"[;&|`]",
                r"\$\(.*\)",
                r"`.*`",
            ],
        }
    
    def _load_anomaly_thresholds(self) -> Dict:
        """Load anomaly detection thresholds"""
        return {
            'failed_logins': 5,  # Alert after 5 failed logins in 5 minutes
            'rapid_requests': 100,  # Alert after 100 requests in 1 minute
            'large_export': 1000,  # Alert on exports > 1000 records
            'unusual_hours': True,  # Alert on access outside 6am-10pm
            'new_location': True,  # Alert on access from new IP
            'multiple_devices': 3,  # Alert on >3 simultaneous devices
        }
    
    def monitor_logs(self, check_interval: int = 60):
        """Continuously monitor audit logs for threats"""
        print(f"🔒 Security Monitor started - checking every {check_interval} seconds")
        
        while True:
            try:
                # Get recent logs (last 5 minutes)
                recent_logs = self._get_recent_logs(minutes=5)
                
                # Analyze logs
                threats = self._detect_threats(recent_logs)
                anomalies = self._detect_anomalies(recent_logs)
                
                # Process alerts
                if threats:
                    self._handle_threats(threats)
                
                if anomalies:
                    self._handle_anomalies(anomalies)
                
                # Update baselines
                self._update_baselines(recent_logs)
                
                # Sleep until next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("🔒 Security Monitor stopped")
                break
            except Exception as e:
                print(f"❌ Error in security monitor: {e}")
                time.sleep(check_interval)
    
    def _get_recent_logs(self, minutes: int = 5) -> List[Dict]:
        """Get recent audit logs"""
        logs = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        if not os.path.exists(self.audit_log_dir):
            return logs
        
        # Get today's log file
        log_date = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(self.audit_log_dir, f"audit_{log_date}.jsonl")
        
        if not os.path.exists(log_file):
            return logs
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        log_entry = json.loads(line)
                        log_time = datetime.fromisoformat(log_entry.get('timestamp', ''))
                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return logs
    
    def _detect_threats(self, logs: List[Dict]) -> List[Dict]:
        """Detect security threats in logs"""
        threats = []
        
        for log in logs:
            endpoint = log.get('endpoint', '')
            method = log.get('method', '')
            ip_address = log.get('ip_address', '')
            user_agent = log.get('user_agent', '')
            
            # Check for SQL injection
            if self._check_patterns(endpoint + user_agent, self.threat_patterns['sql_injection']):
                threats.append({
                    'type': 'sql_injection_attempt',
                    'severity': 'high',
                    'log': log,
                    'description': f'SQL injection attempt detected from {ip_address}'
                })
            
            # Check for XSS
            if self._check_patterns(endpoint + user_agent, self.threat_patterns['xss']):
                threats.append({
                    'type': 'xss_attempt',
                    'severity': 'high',
                    'log': log,
                    'description': f'XSS attempt detected from {ip_address}'
                })
            
            # Check for path traversal
            if self._check_patterns(endpoint, self.threat_patterns['path_traversal']):
                threats.append({
                    'type': 'path_traversal_attempt',
                    'severity': 'high',
                    'log': log,
                    'description': f'Path traversal attempt detected from {ip_address}'
                })
            
            # Check for command injection
            if self._check_patterns(endpoint + user_agent, self.threat_patterns['command_injection']):
                threats.append({
                    'type': 'command_injection_attempt',
                    'severity': 'high',
                    'log': log,
                    'description': f'Command injection attempt detected from {ip_address}'
                })
        
        return threats
    
    def _detect_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Detect anomalous behavior"""
        anomalies = []
        
        # Group by user
        user_logs = defaultdict(list)
        for log in logs:
            user_id = log.get('user_id') or log.get('email', 'unknown')
            user_logs[user_id].append(log)
        
        for user_id, user_log_list in user_logs.items():
            # Check failed login attempts
            failed_logins = [l for l in user_log_list if l.get('event_type') == 'authentication' and l.get('status') == 'failure']
            if len(failed_logins) >= self.anomaly_thresholds['failed_logins']:
                anomalies.append({
                    'type': 'brute_force_attempt',
                    'severity': 'high',
                    'user_id': user_id,
                    'count': len(failed_logins),
                    'description': f'{len(failed_logins)} failed login attempts for {user_id}'
                })
            
            # Check rapid requests
            if len(user_log_list) >= self.anomaly_thresholds['rapid_requests']:
                anomalies.append({
                    'type': 'rapid_requests',
                    'severity': 'medium',
                    'user_id': user_id,
                    'count': len(user_log_list),
                    'description': f'{len(user_log_list)} requests in 5 minutes from {user_id}'
                })
            
            # Check large data exports
            exports = [l for l in user_log_list if l.get('event_type') == 'data_access' and l.get('endpoint') == '/api/user/data-export']
            for export in exports:
                record_count = export.get('details', {}).get('record_count', 0)
                if record_count >= self.anomaly_thresholds['large_export']:
                    anomalies.append({
                        'type': 'large_data_export',
                        'severity': 'medium',
                        'user_id': user_id,
                        'count': record_count,
                        'description': f'Large data export: {record_count} records by {user_id}'
                    })
            
            # Check unusual access hours (outside 6am-10pm UTC)
            current_hour = datetime.utcnow().hour
            if self.anomaly_thresholds['unusual_hours'] and (current_hour < 6 or current_hour > 22):
                anomalies.append({
                    'type': 'unusual_access_hours',
                    'severity': 'low',
                    'user_id': user_id,
                    'hour': current_hour,
                    'description': f'Access outside normal hours ({current_hour}:00 UTC) by {user_id}'
                })
        
        return anomalies
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any threat pattern"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _handle_threats(self, threats: List[Dict]):
        """Handle detected threats"""
        for threat in threats:
            severity = threat.get('severity', 'medium')
            description = threat.get('description', 'Unknown threat')
            
            print(f"🚨 THREAT DETECTED [{severity.upper()}]: {description}")
            
            # Log threat
            self._log_security_event('threat_detected', severity, description, threat.get('log'))
            
            # Send alert for high/critical severity
            if severity in ['high', 'critical']:
                self._send_alert(severity, description, threat)
    
    def _handle_anomalies(self, anomalies: List[Dict]):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'low')
            description = anomaly.get('description', 'Unknown anomaly')
            
            print(f"⚠️ ANOMALY DETECTED [{severity.upper()}]: {description}")
            
            # Log anomaly
            self._log_security_event('anomaly_detected', severity, description, None)
            
            # Send alert for high severity
            if severity == 'high':
                self._send_alert(severity, description, anomaly)
    
    def _log_security_event(self, event_type: str, severity: str, description: str, log_data: Optional[Dict]):
        """Log security event to audit log"""
        from security.audit import log_security_event
        
        log_security_event(
            event_type=event_type,
            severity=severity,
            description=description,
            details={'log_data': log_data} if log_data else {}
        )
    
    def _send_alert(self, severity: str, description: str, event_data: Dict):
        """Send security alert"""
        # For now, just print - can be extended to email/SMS
        alert_message = f"""
        🚨 SECURITY ALERT [{severity.upper()}]
        
        {description}
        
        Time: {datetime.utcnow().isoformat()}
        Event Data: {json.dumps(event_data, indent=2)}
        """
        
        print(alert_message)
        
        # TODO: Send email if alert_email is configured
        # TODO: Send SMS if configured
        # TODO: Send to Slack webhook if configured
    
    def _update_baselines(self, logs: List[Dict]):
        """Update user behavior baselines"""
        for log in logs:
            user_id = log.get('user_id') or log.get('email', 'unknown')
            
            if user_id not in self.user_baselines:
                self.user_baselines[user_id] = {
                    'ips': set(),
                    'user_agents': set(),
                    'endpoints': set(),
                    'request_count': 0,
                    'last_seen': datetime.utcnow()
                }
            
            baseline = self.user_baselines[user_id]
            baseline['ips'].add(log.get('ip_address', ''))
            baseline['user_agents'].add(log.get('user_agent', ''))
            baseline['endpoints'].add(log.get('endpoint', ''))
            baseline['request_count'] += 1
            baseline['last_seen'] = datetime.utcnow()

def run_security_monitor():
    """Run the security monitoring bot"""
    from config import settings
    
    monitor = SecurityMonitor(
        audit_log_dir="audit_logs",
        alert_email=settings.SECURITY_ALERT_EMAIL
    )
    
    monitor.monitor_logs(check_interval=60)  # Check every 60 seconds

if __name__ == "__main__":
    run_security_monitor()
