## MODIFIED Requirements

### Requirement: Google login entry point
The application MUST offer a Google sign-in action without preventing anonymous visitors from using album features.
#### Scenario: Unauthenticated visitor requests a feature page
- Given a visitor is not authenticated
- When they request `/`, `/search`, `/process`, `/run_search`, `/save_albums`, or `/timeline`
- Then the requested page renders normally without redirecting to `/login`
- And the page surfaces a “Sign in with Google” link or button when Google OAuth is configured

### Requirement: OAuth configuration validation
The application MUST detect missing Google OAuth credentials during startup and continue running while warning the operator.
#### Scenario: Application starts without Google credentials
- Given the Flask app starts without `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, or `GOOGLE_REDIRECT_URI`
- When initialization runs
- Then the app logs or prints a clear warning about optional Google sign-in being disabled
- And the server continues serving requests without raising a fatal error

## ADDED Requirements

### Requirement: Optional sign-in status display
When a visitor is authenticated, the UI MUST show their Google profile info, otherwise it MUST keep headers neutral.
#### Scenario: Authenticated user visits the app
- Given a user has an authenticated session
- When they view `/`, `/search`, or `/timeline`
- Then their Google display name (and avatar when available) is shown in the header along with a sign-out action

#### Scenario: Anonymous visitor uses the app
- Given a visitor is not authenticated
- When they view `/`, `/search`, or `/timeline`
- Then no user-specific name or avatar is rendered
- And a generic “Sign in” call-to-action is shown only if Google OAuth is properly configured

## REMOVED Requirements

### Requirement: Protect JSON endpoints for authenticated use
Anonymous sessions are now allowed to use album APIs, so enforcing authentication on `/save_albums` is no longer required.
