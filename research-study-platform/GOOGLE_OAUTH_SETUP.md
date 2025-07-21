# Google OAuth Setup Guide

This guide will help you configure real Google OAuth credentials for both registration and login functionality.

## Prerequisites

- A Google Cloud Console account
- Access to your domain (for production setup)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Identity API for your project

## Step 2: Configure OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have Google Workspace)
3. Fill in required information:
   - App name: "Research Study Platform"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes (if needed):
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
5. Save and continue

## Step 3: Create OAuth 2.0 Client ID

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Web application" as application type
4. Configure the client:
   - **Name**: "Research Platform Web Client"
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
5. Click "Create"
6. Copy the Client ID (looks like: `123456789-abc123.apps.googleusercontent.com`)

## Step 4: Update Environment Variables

### Backend Configuration (.env)
```bash
# Replace with your real Google OAuth2 Client ID
GOOGLE_OAUTH2_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

### Frontend Configuration (frontend/.env.local)
```bash
# Replace with the same Google OAuth2 Client ID
REACT_APP_GOOGLE_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

## Step 5: Update Railway Environment Variables (Production)

For Railway deployment, add the environment variable:
```bash
GOOGLE_OAUTH2_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

## Step 6: Test the Integration

1. Start your development servers:
   ```bash
   # Backend
   cd research-study-platform
   ./venv/bin/python manage.py runserver

   # Frontend
   cd frontend
   npm run dev
   ```

2. Navigate to `http://localhost:3000/register` or `http://localhost:3000/login`
3. Click "Sign up with Google" or "Sign in with Google"
4. Complete the Google OAuth flow
5. Verify that the user is created/logged in successfully

## Security Notes

- **Never commit real credentials to version control**
- The Client ID is public and safe to expose in frontend code
- No Client Secret is needed for this OAuth flow (frontend-only)
- The backend verifies the Google token server-side for security

## Troubleshooting

### "Error 400: redirect_uri_mismatch"
- Ensure your authorized redirect URIs in Google Console match exactly
- Check that you're using the correct protocol (http vs https)
- Verify the port numbers match

### "Error 403: access_denied"
- Verify your OAuth consent screen is properly configured
- Check that the app is not in testing mode if using external users
- Ensure the user's email domain is allowed

### Frontend Error: "Google Client ID not configured"
- Verify `REACT_APP_GOOGLE_CLIENT_ID` is set in your environment
- Restart the development server after changing environment variables
- Check browser console for detailed error messages

### Backend Error: "Invalid Google token"
- Ensure `GOOGLE_OAUTH2_CLIENT_ID` matches the frontend configuration
- Verify the backend has the correct Google Auth libraries installed
- Check Django logs for detailed error messages

## Production Considerations

1. **Domain Configuration**: Update authorized origins and redirect URIs with your production domain
2. **HTTPS**: Ensure your production site uses HTTPS
3. **Environment Variables**: Set credentials in your hosting platform's environment variable settings
4. **Error Handling**: Monitor logs for authentication errors in production