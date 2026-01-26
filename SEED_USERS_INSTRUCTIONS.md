# How to Seed Users in the Database

The API requires users to be in the database before they can log in. Here's how to create them:

## Option 1: Run Seed Script Locally (for local development)

```bash
python3 seed_users.py
```

This will create all 6 users with their passwords from the credentials document.

## Option 2: Enable Auto-Seed on Render (for production)

1. Go to your Render dashboard
2. Navigate to your service's Environment variables
3. Add a new environment variable:
   - Key: `AUTO_SEED_USERS`
   - Value: `True`
4. Redeploy the service

The app will automatically seed users on startup if the database is empty.

## Option 3: Run Seed Script on Render (one-time)

If you have SSH access to Render, you can run:

```bash
python3 seed_users.py
```

## User Credentials

The seed script creates these users:

1. **Hope Gilbert** - hg@mawneypartners.com - Password: `Mawney2024!HopeSecure`
2. **Joshua Trister** - jt@mawneypartners.com - Password: `Trister2024!JoshSecure`
3. **Rachel Trister** - finance@mawneypartners.com - Password: `Finance2024!RachelSecure`
4. **Jack Dalby** - jd@mawneypartners.com - Password: `Dalby2024!JackSecure`
5. **Harry Edleman** - he@mawneypartners.com - Password: `Edleman2024!HarrySecure`
6. **Tyler Johnson Thomas** - tjt@mawneypartners.com - Password: `Thomas2024!TylerSecure`

## Notes

- The seed script will update passwords if users already exist
- Users are created with `is_active=True` and `is_deleted=False`
- All users have the `['user']` role by default
