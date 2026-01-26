# Push Notification Setup for Industry Moves

## What Was Added

1. **Push Notification Functions** (lines ~2852-2940 in app.py):
   - `get_apns_client()` - Initializes Apple Push Notification service client
   - `send_push_notification()` - Sends a push notification to a device
   - `notify_all_users_about_move()` - Sends notifications to all users when a move is created

2. **Updated POST /api/industry-moves Endpoint**:
   - Now handles both JSON and multipart/form-data requests
   - Supports image uploads
   - Automatically sends push notifications to all users (except the creator) when a move is created
   - Fixed bug: Changed `email` to `user_email` variable

3. **Imports Added**:
   - `from apns2.client import APNsClient`
   - `from apns2.payload import Payload`
   - `from apns2.credentials import TokenCredentials`

## Environment Variables Required

Add these to your `.env` file or environment:

```bash
# Apple Push Notification Service Configuration
APNS_KEY_ID=your_key_id_here          # Your APNs Key ID from Apple Developer
APNS_TEAM_ID=your_team_id_here        # Your Apple Team ID
APNS_KEY_PATH=apns_key.p8              # Path to your .p8 key file
APNS_TOPIC=com.mawneypartners.app      # Your app's bundle identifier
APNS_USE_SANDBOX=False                 # Set to True for development, False for production
```

## How to Get APNs Credentials

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/authkeys/list)
2. Create a new Key with "Apple Push Notifications service (APNs)" enabled
3. Download the `.p8` key file
4. Note the Key ID and your Team ID
5. Place the `.p8` file in your API directory (or update `APNS_KEY_PATH`)

## How It Works

1. When a user creates a move via `POST /api/industry-moves`:
   - The move is saved to `user_industry_moves`
   - `notify_all_users_about_move()` is called
   - This function iterates through all registered device tokens
   - Sends a push notification to each user (except the creator)
   - Notification includes: "🔄 New Market Move" with move details

2. Device tokens are registered via the existing `/api/register-device-token` endpoint

## Testing

1. Register device tokens for test users
2. Create a move through the API
3. Check that all other users receive push notifications
4. Check API logs for notification status

## Fallback Behavior

- If APNs credentials are not configured, the API will log a warning but continue working
- If push notifications fail, the move creation still succeeds (notifications are non-blocking)
- Local notifications in the iOS app will still work as a fallback

## Notes

- Push notifications require the app to be properly configured with APNs certificates
- The notification will appear on users' devices even when the app is closed
- Make sure your app's bundle ID matches `APNS_TOPIC`
