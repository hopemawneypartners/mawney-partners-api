# Security Testing Guide

## Quick Test Checklist

### ✅ Step 1: Test Encryption (2 minutes)
```bash
python3 -c "from security.encryption import encrypt_field, decrypt_field; test='sensitive data'; enc=encrypt_field(test); dec=decrypt_field(enc); print('✅ Encryption works!' if test==dec else '❌ Encryption failed')"
```

### ✅ Step 2: Test Authentication (5 minutes)

**Register a user:**
```bash
curl -X POST https://mawney-daily-news-api.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123", "name": "Test User"}'
```

**Login:**
```bash
curl -X POST https://mawney-daily-news-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

Save the `access_token` from the response.

**Test protected endpoint:**
```bash
curl -X GET "https://mawney-daily-news-api.onrender.com/api/compensations?email=test@example.com" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### ✅ Step 3: Test GDPR Endpoints (3 minutes)

**Export data:**
```bash
curl -X GET https://mawney-daily-news-api.onrender.com/api/user/data-export \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Get audit logs:**
```bash
curl -X GET "https://mawney-daily-news-api.onrender.com/api/user/audit-logs?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### ✅ Step 4: Test Rate Limiting (2 minutes)

Try making 100+ requests quickly:
```bash
for i in {1..110}; do
  curl -X GET "https://mawney-daily-news-api.onrender.com/api/compensations?email=test@example.com" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
done
```

You should get rate limit error after 100 requests.

### ✅ Step 5: Test Security Bot (5 minutes)

**Start the security bot:**
```bash
python3 security_bot/monitor.py
```

**Trigger a threat (in another terminal):**
```bash
# Try SQL injection
curl -X GET "https://mawney-daily-news-api.onrender.com/api/compensations?email=test@example.com' OR '1'='1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

The security bot should detect and alert.

## Full Test Suite

### Authentication Tests

1. **Register** - Create new user account
2. **Login** - Get access and refresh tokens
3. **Refresh Token** - Use refresh token to get new access token
4. **Logout** - Revoke tokens
5. **Invalid Credentials** - Should fail
6. **Expired Token** - Should require refresh

### Authorization Tests

1. **Access Own Data** - Should succeed
2. **Access Other User's Data** - Should fail (403)
3. **Admin Access** - Admin should access all data
4. **Missing Token** - Should fail (401)

### Encryption Tests

1. **Encrypt/Decrypt** - Data should encrypt and decrypt correctly
2. **Database Storage** - Encrypted data in database
3. **API Response** - Decrypted data in API responses

### GDPR Tests

1. **Data Export** - Export all user data
2. **Data Deletion** - Soft delete user data
3. **Audit Logs** - Retrieve user's audit logs

### Security Bot Tests

1. **Threat Detection** - SQL injection, XSS, etc.
2. **Anomaly Detection** - Brute force, rapid requests
3. **Alerting** - Alerts sent for threats

## Expected Results

- ✅ All authentication endpoints work
- ✅ Protected endpoints require authentication
- ✅ Users can only access their own data
- ✅ Sensitive data is encrypted
- ✅ All access is logged
- ✅ Rate limiting works
- ✅ Security bot detects threats

## Troubleshooting

**"Module not found" errors:**
- Run: `pip install -r requirements.txt`

**"Database error":**
- Run: `python3 -c "from database.models import init_db; init_db()"`

**"Encryption key error":**
- Check `.env` file has `ENCRYPTION_KEY` set

**"JWT error":**
- Check `.env` file has `JWT_SECRET_KEY` set
