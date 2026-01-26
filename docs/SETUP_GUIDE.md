# Security Setup Guide

This guide will help you set up the comprehensive security system for the Mawney Partners API.

## Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL** (optional, for production) or **SQLite** (for development)
3. **Redis** (optional, for rate limiting and token blacklist)

## Step 1: Install Dependencies

```bash
cd mawney-api-clean
pip install -r requirements.txt
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Application
DEBUG=False
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32

# Database (choose one)
# Option A: PostgreSQL (production)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Option B: SQLite (development)
USE_SQLITE=True
SQLITE_PATH=mawney_api.db

# Redis (optional, for rate limiting)
REDIS_URL=redis://localhost:6379/0
# OR
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here-generate-with-openssl-rand-hex-32
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days

# Encryption Key (IMPORTANT: Generate a proper key!)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-encryption-key-here

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_AUTH_ATTEMPTS=5

# Base URL
BASE_URL=https://mawney-daily-news-api.onrender.com

# Sentry (optional, for error tracking)
SENTRY_DSN=your-sentry-dsn-here
SENTRY_ENVIRONMENT=production

# Security Bot
SECURITY_BOT_ENABLED=True
SECURITY_ALERT_EMAIL=your-email@example.com
SECURITY_ALERT_SMS=your-phone-number

# GDPR
AUDIT_LOG_RETENTION_DAYS=2555  # 7 years
DATA_DELETION_RETENTION_DAYS=30  # 30 days soft delete

# MFA
MFA_ISSUER_NAME=Mawney Partners
```

## Step 3: Generate Security Keys

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Generate JWT Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**⚠️ IMPORTANT:** Store these keys securely! Never commit them to git.

## Step 4: Set Up Database

### Option A: PostgreSQL (Production)

1. **Create PostgreSQL database:**
   ```bash
   createdb mawney_api
   ```

2. **Install PostgreSQL client libraries:**
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   ```

3. **Enable pgcrypto extension:**
   ```sql
   psql mawney_api
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   ```

4. **Update .env:**
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/mawney_api
   ```

### Option B: SQLite (Development)

1. **Update .env:**
   ```
   USE_SQLITE=True
   SQLITE_PATH=mawney_api.db
   ```

2. **SQLite will be created automatically**

## Step 5: Set Up Redis (Optional)

### Option A: Local Redis

1. **Install Redis:**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

2. **Update .env:**
   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ```

### Option B: Render.com Redis (Free Tier)

1. **Create Redis instance on Render.com**
2. **Update .env with Redis URL from Render**

### Option C: Skip Redis (Fallback)

- Rate limiting will use in-memory storage (not recommended for production)
- Token blacklist will use in-memory storage

## Step 6: Initialize Database

```bash
python -c "from database.models import init_db; init_db()"
```

Or create a script:

```python
# init_database.py
from database.models import init_db
init_db()
print("Database initialized!")
```

Run:
```bash
python init_database.py
```

## Step 7: Set Up Sentry (Optional)

1. **Create Sentry account:** https://sentry.io
2. **Create new project** (Flask)
3. **Copy DSN** to `.env`:
   ```
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

## Step 8: Test the Setup

Create a test script:

```python
# test_security.py
from security.auth import create_access_token, create_refresh_token
from security.encryption import encrypt_field, decrypt_field
from security.audit import log_event

# Test encryption
test_data = "sensitive data"
encrypted = encrypt_field(test_data)
decrypted = decrypt_field(encrypted)
print(f"Encryption test: {test_data == decrypted}")

# Test JWT
token = create_access_token("user123", "test@example.com")
print(f"JWT token created: {token[:50]}...")

# Test audit logging
log_event("test_event", user_id="user123", email="test@example.com")
print("Audit logging test: OK")
```

Run:
```bash
python test_security.py
```

## Step 9: Update app.py

The main `app.py` file needs to be updated to use the security system. This will be done in the next phase.

## Step 10: Deploy to Render.com

1. **Set environment variables in Render.com dashboard:**
   - Go to your Render service
   - Settings → Environment
   - Add all variables from `.env`

2. **Add PostgreSQL database (if using):**
   - Create new PostgreSQL database on Render
   - Copy connection string to `DATABASE_URL`

3. **Add Redis (if using):**
   - Create new Redis instance on Render
   - Copy connection string to `REDIS_URL`

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Add comprehensive security system"
   git push origin main
   ```

## Troubleshooting

### Redis Connection Error
- Check Redis is running: `redis-cli ping`
- Verify connection details in `.env`
- System will fall back to in-memory if Redis unavailable

### Database Connection Error
- Verify database credentials
- Check database is running
- For PostgreSQL: `psql -U user -d mawney_api -c "SELECT 1"`

### Encryption Key Error
- Ensure encryption key is properly formatted (base64)
- Generate new key if needed
- **Never change encryption key after data is encrypted!**

## Next Steps

1. ✅ Set up environment variables
2. ✅ Initialize database
3. ⏭️ Update API endpoints with security
4. ⏭️ Create authentication endpoints
5. ⏭️ Set up security monitoring bot
6. ⏭️ Configure Cloudflare (optional)

## Security Checklist

- [ ] All environment variables set
- [ ] Strong secret keys generated
- [ ] Database initialized
- [ ] Redis configured (optional)
- [ ] Encryption key generated
- [ ] Sentry configured (optional)
- [ ] Environment variables added to Render.com
- [ ] Database created on Render.com (if using)
- [ ] Redis created on Render.com (if using)
- [ ] Test script runs successfully

## Support

If you encounter issues:
1. Check logs: `tail -f audit_logs/audit_*.jsonl`
2. Check environment variables: `python -c "from config import settings; print(settings.__dict__)"`
3. Test individual components (see test script above)
