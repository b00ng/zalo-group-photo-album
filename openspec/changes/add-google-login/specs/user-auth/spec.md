## ADDED Requirements

### Requirement: Google login entry point
The application MUST funnel unauthenticated visitors to a dedicated login screen with a Google sign-in affordance before allowing access to album features.
#### Scenario: Unauthenticated visitor requests a protected page
- Given a visitor is not authenticated
- When they request `/`, `/search`, `/process`, `/run_search`, or `/save_albums`
- Then they are redirected to `/login`
- And `/login` renders a “Continue with Google” action that begins Google sign-in

### Requirement: Start Google OAuth authorization
The system MUST initiate Google’s OAuth 2.0 Authorization Code flow with the correct scopes and CSRF protections when a visitor chooses to continue with Google.
#### Scenario: User clicks Continue with Google
- Given an unauthenticated visitor is on `/login`
- When they activate the “Continue with Google” action
- Then the browser is redirected to Google’s OAuth 2.0 authorization endpoint with scopes `openid email profile`
- And the request includes a cryptographically random `state` value persisted server-side for this user

### Requirement: Handle OAuth callback and create session
A successful Google callback MUST produce an authenticated server-side session populated with the user’s core profile attributes, while failures keep the visitor unauthenticated.
#### Scenario: Google redirects back with a valid authorization code
- Given Google redirects to `/auth/google/callback` with a matching `state`
- When the backend exchanges the code for tokens
- Then the ID token audience is validated against the configured client ID
- And the session stores the user’s Google subject, email, display name, and profile picture URL
- And the user is redirected back to their originally requested page or `/`

#### Scenario: Google callback fails
- Given Google redirects to `/auth/google/callback` without a code or with state mismatch
- When the backend detects the error
- Then no authenticated session is created
- And the user is shown an error message on `/login` with a way to retry

### Requirement: Protect JSON endpoints for authenticated use
Authenticated status MUST be enforced consistently for background requests so that album creation APIs cannot be called anonymously.
#### Scenario: Unauthenticated XHR calls a protected endpoint
- Given the `/save_albums` endpoint receives a request without an authenticated session
- When the backend handles the request
- Then it responds with HTTP 401 and a JSON error indicating authentication is required

### Requirement: Signed-in experience and sign-out
Once authenticated, users MUST see who is signed in and MUST be able to terminate their own session.
#### Scenario: Authenticated user visits the app
- Given a user has an authenticated session
- When they view `/` or `/search`
- Then their Google display name (and avatar when available) is shown in the header along with a sign-out action

#### Scenario: User signs out
- Given a user clicks the sign-out action
- When the backend processes `/logout`
- Then the session is cleared
- And the user is redirected to `/login`

### Requirement: OAuth configuration validation
The application MUST detect missing Google OAuth credentials during startup and refuse to run with a helpful error.
#### Scenario: Application starts without Google credentials
- Given the Flask app starts without `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, or `GOOGLE_REDIRECT_URI`
- When initialization runs
- Then the startup fails fast with a clear log or error explaining the missing configuration
