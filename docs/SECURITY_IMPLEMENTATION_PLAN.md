# Comprehensive Security Implementation Plan (Option 1)

## Overview

This plan implements enterprise-grade security for the Mawney Partners API, ensuring GDPR compliance and protection of sensitive financial data.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS Application                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  JWT Tokens  │  │  MFA (TOTP)  │  │ Certificate  │      │
│  │  (Access +  │  │  + Biometric │  │   Pinning    │      │
│  │   Refresh)   │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/TLS 1.3
                            │
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare (DDoS Protection + WAF)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Rate Limiting│  │   WAF Rules  │  │  IP Filter   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│              Flask API (Render.com)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Authentication Layer                                 │   │
│  │  - JWT Validation                                     │   │
│  │  - Token Refresh                                      │   │
│  │  - MFA Verification                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Authorization Layer                                 │   │
│  │  - RBAC (Role-Based Access Control)                  │   │
│  │  - Data Ownership Verification                       │   │
│  │  - Permission Checks                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Encryption Layer                                     │   │
│  │  - Field-level Encryption (AES-256)                  │   │
│  │  - Key Management                                    │   │
│  │  - Encrypted Database                                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Audit & Logging Layer                                │   │
│  │  - All API calls logged                              │   │
│  │  - Data access tracking                              │   │
│  │  - Security events                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│              Database (PostgreSQL with Encryption)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Encrypted     │  │ Audit Logs  │  │ User Data    │      │
│  │ User Data     │  │ (Immutable) │  │ (Encrypted)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│              Security Monitoring Stack                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Sentry       │  │ Custom Bot  │  │ Alert System │      │
│  │ (Errors)     │  │ (Threats)    │  │ (Email/SMS)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Authentication & Authorization

#### JWT (JSON Web Tokens)
**Purpose:** Stateless authentication that doesn't require server-side sessions

**Implementation:**
- **Access Tokens:** Short-lived (15-30 minutes)
  - Contains: user_id, email, roles, permissions
  - Signed with RS256 (asymmetric) or HS256 (symmetric)
  - Stored in iOS Keychain (secure storage)
  
- **Refresh Tokens:** Long-lived (7-30 days)
  - Stored securely on server (hashed)
  - Used to generate new access tokens
  - Can be revoked (for logout, security breach)
  - Rotated on each use (old token invalidated)

**Token Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["user"],
  "permissions": ["read:compensation", "write:call_notes"],
  "iat": 1234567890,
  "exp": 1234567890,
  "jti": "unique_token_id"
}
```

**Security Features:**
- Token rotation (new refresh token on each refresh)
- Token blacklisting (for revoked tokens)
- IP address validation (optional)
- Device fingerprinting (optional)

#### Multi-Factor Authentication (MFA)
**TOTP (Time-based One-Time Password)**
- Google Authenticator / Authy compatible
- 6-digit codes, 30-second window
- Backup codes for recovery
- QR code generation for setup

**Biometric Authentication** (Already in iOS app)
- Face ID / Touch ID
- Used for app unlock
- Doesn't replace server-side auth

**SMS Backup Codes**
- 10 one-time codes
- For account recovery
- Regenerated on use

#### OAuth 2.0 (Optional)
- For third-party integrations
- Not required for initial implementation

---

### 2. Data Protection

#### Encryption at Rest

**Database Encryption:**
- **PostgreSQL with pgcrypto extension**
  - Transparent Data Encryption (TDE)
  - Encrypt entire database files
  - Automatic encryption/decryption

**Field-Level Encryption:**
- **Sensitive fields encrypted separately:**
  - Compensation data (salary, bonus, equity)
  - Call notes (transcripts, summaries)
  - User profiles (email, phone)
  - Device tokens

**Encryption Method:**
- **AES-256-GCM** (Galois/Counter Mode)
  - Authenticated encryption
  - Prevents tampering
  - Industry standard

**Key Management:**
- **Option A: Environment Variables** (Simple)
  - Encryption key in `ENCRYPTION_KEY` env var
  - Rotated manually
  - Good for MVP

- **Option B: AWS KMS** (Production)
  - Managed key service
  - Automatic rotation
  - Audit trail
  - Cost: ~$1/month per key

- **Option C: HashiCorp Vault** (Enterprise)
  - Self-hosted key management
  - Advanced features
  - Requires infrastructure

**File Encryption:**
- CV files encrypted before storage
- Call note attachments encrypted
- Temporary files encrypted

#### Encryption in Transit
- **TLS 1.3** (already provided by Render.com)
- **Certificate Pinning** in iOS app
  - Prevents man-in-the-middle attacks
  - Validates server certificate
  - Hardcoded certificate fingerprints

#### Key Rotation Strategy
- Encryption keys rotated quarterly
- Old keys retained for decryption (data migration)
- New data uses new keys
- Gradual re-encryption of old data

---

### 3. Access Control

#### Role-Based Access Control (RBAC)

**Roles:**
- **Admin:** Full access, user management
- **User:** Own data access, read/write
- **Read-only:** View-only access (for auditors)

**Permissions:**
```python
PERMISSIONS = {
    'admin': ['*'],  # All permissions
    'user': [
        'read:own_compensation',
        'write:own_compensation',
        'read:own_call_notes',
        'write:own_call_notes',
        'read:own_todos',
        'write:own_todos',
    ],
    'read-only': [
        'read:own_compensation',
        'read:own_call_notes',
        'read:own_todos',
    ]
}
```

**Data Ownership Verification:**
- Every endpoint checks: `user_id == data.owner_id`
- Prevents users accessing other users' data
- Enforced at database query level

**IP Whitelisting** (Optional)
- Restrict API access to known IPs
- Useful for internal tools
- Not recommended for mobile apps

---

### 4. Monitoring & Security Bots

#### Security Information and Event Management (SIEM)

**Custom Security Bot** (Python)
**Purpose:** Real-time threat detection and monitoring

**Features:**
1. **Anomaly Detection**
   - Unusual access patterns
   - Access from new locations
   - Access outside business hours
   - Multiple failed login attempts
   - Rapid API calls (potential scraping)

2. **Threat Detection**
   - Brute force attacks
   - SQL injection attempts
   - XSS attempts
   - Unauthorized access attempts
   - Token theft attempts

3. **Data Access Monitoring**
   - Large data exports
   - Unusual data access patterns
   - Access to sensitive endpoints
   - Multiple device logins

4. **Automated Response**
   - Temporary account lockout
   - Token revocation
   - Alert notifications
   - Security report generation

**Implementation:**
- Python script running continuously
- Monitors API logs in real-time
- Uses machine learning for anomaly detection (optional)
- Sends alerts via email/SMS/Slack

**Alert Types:**
- **Critical:** Immediate action required (breach, attack)
- **High:** Security concern (multiple failed logins)
- **Medium:** Unusual activity (new location)
- **Low:** Informational (new device)

#### Sentry Integration
**Purpose:** Error tracking and security monitoring

**Features:**
- Error tracking
- Performance monitoring
- Security event tracking
- Release tracking
- User context

**Setup:**
- Free tier: 5,000 events/month
- Team tier: $26/month (unlimited events)

#### Logging Strategy

**What to Log:**
- All API requests (endpoint, user, timestamp, IP)
- Authentication attempts (success/failure)
- Data access (what data, by whom)
- Data modifications (before/after)
- Security events (failed auth, suspicious activity)
- Admin actions (user creation, permission changes)

**Log Format:**
```json
{
  "timestamp": "2024-01-26T10:30:00Z",
  "event_type": "data_access",
  "user_id": "user123",
  "email": "user@example.com",
  "endpoint": "/api/compensations",
  "method": "GET",
  "ip_address": "192.168.1.1",
  "user_agent": "MawneyApp/1.0",
  "status": "success",
  "data_accessed": "compensation",
  "record_count": 5
}
```

**Log Storage:**
- Immutable audit logs (cannot be modified)
- 7-year retention (GDPR requirement)
- Encrypted storage
- Regular backups

---

### 5. GDPR Compliance

#### Data Subject Rights

**Right to Access (Article 15)**
- Endpoint: `GET /api/user/data-export`
- Returns all user data in JSON format
- Includes: compensation, call notes, todos, chats, profile

**Right to Deletion (Article 17)**
- Endpoint: `DELETE /api/user/data`
- Soft delete (mark as deleted, retain for 30 days)
- Hard delete after retention period
- Audit log entry created

**Right to Rectification (Article 16)**
- Endpoint: `PUT /api/user/profile`
- Update user data
- Audit log entry created

**Right to Data Portability (Article 20)**
- Same as data export
- Machine-readable format (JSON)

#### Data Processing Records
- Document what data is collected
- Why it's collected (legal basis)
- How long it's retained
- Who has access
- Security measures

#### Consent Management
- Explicit consent for data processing
- Consent withdrawal mechanism
- Consent audit trail
- Privacy policy acceptance

#### Data Breach Detection & Notification
- Automated breach detection (security bot)
- 72-hour notification process
- Incident response plan
- Breach log

#### Privacy by Design
- Default privacy settings (most restrictive)
- Data minimization (only collect necessary data)
- Purpose limitation (use data only for stated purpose)
- Storage limitation (delete old data)

---

### 6. Rate Limiting & DDoS Protection

#### Rate Limiting

**Per-User Limits:**
- 100 requests/minute (normal usage)
- 10 requests/second (burst protection)
- 1000 requests/hour (daily limit)

**Per-Endpoint Limits:**
- Authentication: 5 attempts/minute
- Data export: 1 request/hour
- File upload: 10 requests/minute

**Implementation:**
- Flask-Limiter with Redis backend
- Token bucket algorithm
- Sliding window rate limiting

**Response:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0
}
```

#### DDoS Protection

**Cloudflare** (Recommended)
- Free tier: Basic DDoS protection
- Pro tier ($20/month): Advanced DDoS, WAF, rate limiting
- Business tier ($200/month): Enterprise features

**Features:**
- Automatic DDoS mitigation
- Web Application Firewall (WAF)
- Bot detection
- IP reputation filtering
- Geographic filtering

**Setup:**
1. Point domain to Cloudflare
2. Configure DNS
3. Enable DDoS protection
4. Configure WAF rules
5. Set up rate limiting

---

### 7. Input Validation & Sanitization

#### Request Validation

**Schema Validation:**
- Pydantic models for request validation
- Type checking
- Required field validation
- Format validation (email, date, etc.)

**Example:**
```python
from pydantic import BaseModel, EmailStr, Field

class CompensationRequest(BaseModel):
    base_salary: float = Field(..., gt=0, le=10000000)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    email: EmailStr
```

**Input Sanitization:**
- HTML escaping (prevent XSS)
- SQL injection prevention (parameterized queries)
- Path traversal prevention
- Command injection prevention

**File Upload Security:**
- File type validation (whitelist)
- File size limits (10MB max)
- Virus scanning (ClamAV)
- Content validation
- Filename sanitization

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Day 1-3: Authentication Setup**
- [ ] Install dependencies (PyJWT, Flask-JWT-Extended)
- [ ] Create JWT token generation/validation
- [ ] Implement access token (15 min expiry)
- [ ] Implement refresh token (7 day expiry)
- [ ] Token rotation logic
- [ ] Token blacklist (Redis or database)

**Day 4-5: Database Setup**
- [ ] Set up PostgreSQL database (Render.com or external)
- [ ] Install pgcrypto extension
- [ ] Create user table with encrypted fields
- [ ] Create audit log table
- [ ] Migration scripts

**Day 6-7: Basic Access Control**
- [ ] User ownership verification decorator
- [ ] Permission checking middleware
- [ ] Update all endpoints to use auth
- [ ] Test access control

**Day 8-10: Encryption**
- [ ] Set up encryption key management
- [ ] Implement field-level encryption
- [ ] Encrypt existing data (migration)
- [ ] Test encryption/decryption

**Day 11-14: Rate Limiting & Validation**
- [ ] Install Flask-Limiter
- [ ] Set up Redis (for rate limiting)
- [ ] Configure rate limits
- [ ] Add Pydantic validation
- [ ] Input sanitization

---

### Phase 2: GDPR Compliance (Week 3-4)

**Day 15-17: Audit Logging**
- [ ] Create audit log system
- [ ] Log all API requests
- [ ] Log data access
- [ ] Log data modifications
- [ ] Immutable log storage

**Day 18-19: Data Subject Rights**
- [ ] Data export endpoint
- [ ] Data deletion endpoint (soft delete)
- [ ] Data rectification endpoint
- [ ] Test all endpoints

**Day 20-21: Consent Management**
- [ ] Consent tracking system
- [ ] Privacy policy acceptance
- [ ] Consent withdrawal
- [ ] Consent audit trail

**Day 22-24: Data Processing Records**
- [ ] Document data collection
- [ ] Document data retention
- [ ] Document security measures
- [ ] Create privacy policy

**Day 25-28: Testing & Documentation**
- [ ] Test all GDPR features
- [ ] Security testing
- [ ] Documentation
- [ ] User guides

---

### Phase 3: Security Monitoring (Week 5-6)

**Day 29-31: Security Bot Development**
- [ ] Create security monitoring bot
- [ ] Anomaly detection algorithms
- [ ] Threat detection rules
- [ ] Alert system (email/SMS)

**Day 32-33: Sentry Integration**
- [ ] Set up Sentry account
- [ ] Integrate Sentry SDK
- [ ] Configure error tracking
- [ ] Set up alerts

**Day 34-35: Cloudflare Setup**
- [ ] Set up Cloudflare account
- [ ] Configure DNS
- [ ] Enable DDoS protection
- [ ] Configure WAF rules
- [ ] Set up rate limiting

**Day 36-38: Advanced Features**
- [ ] MFA (TOTP) implementation
- [ ] Backup codes
- [ ] Certificate pinning (iOS)
- [ ] IP whitelisting (optional)

**Day 39-42: Testing & Hardening**
- [ ] Penetration testing
- [ ] Security audit
- [ ] Performance testing
- [ ] Documentation
- [ ] Training

---

## Technology Stack

### Backend
- **Flask-JWT-Extended:** JWT authentication
- **PyJWT:** JWT token handling
- **cryptography:** Encryption (Fernet, AES)
- **Flask-Limiter:** Rate limiting
- **Pydantic:** Request validation
- **PostgreSQL + pgcrypto:** Encrypted database
- **Redis:** Rate limiting storage, token blacklist
- **Sentry:** Error tracking
- **python-dotenv:** Environment variables

### iOS App
- **Keychain Services:** Secure token storage
- **CryptoKit:** Certificate pinning
- **LocalAuthentication:** Biometric auth

### Infrastructure
- **Cloudflare:** DDoS protection, WAF
- **Render.com:** Hosting (already set up)
- **PostgreSQL:** Database (Render or external)

---

## Cost Breakdown

### Monthly Costs

**Infrastructure:**
- Render.com: Free tier (or $7/month for paid)
- PostgreSQL: $0-25/month (Render or external)
- Redis: $0-15/month (Render or external)
- Cloudflare: Free tier (or $20/month Pro)

**Services:**
- Sentry: Free tier (or $26/month Team)
- Monitoring: $0-50/month (optional)

**Total: $0-142/month** (depending on tier)

### One-Time Costs
- Development time: 6 weeks
- Security audit: $2,000-5,000 (optional)
- Penetration testing: $3,000-10,000 (optional)

---

## Security Bot Architecture

### Custom Security Bot

**File Structure:**
```
security_bot/
├── __init__.py
├── main.py              # Main bot loop
├── detectors/
│   ├── anomaly.py       # Anomaly detection
│   ├── threat.py        # Threat detection
│   └── breach.py       # Breach detection
├── alerts/
│   ├── email.py        # Email alerts
│   ├── sms.py          # SMS alerts
│   └── slack.py        # Slack alerts
├── database/
│   └── log_reader.py    # Read audit logs
└── config.py           # Configuration
```

**Detection Rules:**
1. **Failed Login Attempts**
   - 5+ failed logins in 5 minutes → Alert
   - 10+ failed logins in 15 minutes → Lock account

2. **Unusual Access Patterns**
   - Access from new country → Alert
   - Access outside business hours → Alert
   - Access from multiple IPs simultaneously → Alert

3. **Data Access Anomalies**
   - Large data export (>1000 records) → Alert
   - Rapid API calls (>100/minute) → Alert
   - Access to sensitive endpoints → Log + Alert

4. **Security Threats**
   - SQL injection attempt → Block + Alert
   - XSS attempt → Block + Alert
   - Unauthorized access → Block + Alert

**Alert System:**
- Email alerts for all security events
- SMS alerts for critical events
- Slack integration (optional)
- Dashboard for monitoring

---

## Testing Strategy

### Security Testing
- **Penetration Testing:** Hire professional or use tools
- **Vulnerability Scanning:** OWASP ZAP, Bandit
- **Dependency Scanning:** Safety, Snyk
- **Code Review:** Security-focused review

### Functional Testing
- Unit tests for all security functions
- Integration tests for auth flow
- End-to-end tests for GDPR features
- Load testing for rate limiting

---

## Documentation Requirements

1. **Security Policy:** How security is implemented
2. **Privacy Policy:** GDPR compliance, data handling
3. **API Documentation:** Authentication, endpoints
4. **Incident Response Plan:** What to do in case of breach
5. **User Guide:** How to use security features
6. **Developer Guide:** How to maintain security

---

## Next Steps

1. **Review this plan** and confirm approach
2. **Set up infrastructure** (PostgreSQL, Redis)
3. **Begin Phase 1** implementation
4. **Weekly check-ins** to track progress
5. **Security audit** after completion

---

## Questions to Answer

1. **Database:** Render PostgreSQL or external (AWS RDS)?
2. **Redis:** Render Redis or external?
3. **Cloudflare:** Free tier or Pro ($20/month)?
4. **Sentry:** Free tier or Team ($26/month)?
5. **Security Bot:** Custom Python or use existing service?
6. **MFA:** TOTP only or also SMS?
7. **Key Management:** Environment variables or AWS KMS?

Let me know your preferences and I'll start implementing!
