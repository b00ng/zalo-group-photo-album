# Add Google Account Login

## Summary
- Require Google account authentication before accessing photo clustering and search features.
- Introduce an OAuth 2.0 Authorization Code flow that stores a signed-in session with the user's Google profile basics.

## Motivation
- Limit album generation tools to authenticated users so exported content is traceable to a user identity.
- Prepare the application for broader sharing by adding a standard sign-in experience.

## Scope
- Backend endpoints to initiate Google OAuth, handle callbacks, and manage Flask sessions.
- UI updates to prompt unauthenticated visitors to sign in and to show the signed-in user's details with a sign-out action.
- Configuration hooks for Google OAuth credentials and allowed redirect URIs.

## Out of Scope
- Supporting non-Google identity providers or password-based accounts.
- Role-based authorization or differentiating access beyond “signed in” vs “not signed in”.
- Persisting tokens beyond the Flask session or storing refresh tokens server-side.

## User Impact
- Users must sign in with Google before they can upload photos or run clustering/search.
- Signed-in users see their display name/avatar indicator and a sign-out option across pages.

## Dependencies / Tooling
- Likely need `google-auth`/`google-auth-oauthlib` or an equivalent OAuth helper (e.g., `requests-oauthlib`) added to `requirements.txt`.
- Application must be configured with `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and redirect URL (likely `/auth/google/callback`).

## Risks & Mitigations
- **OAuth misconfiguration**: add validation on app start that credentials are present; log actionable errors.
- **Session forgery**: use Google-provided ID token claims and `state` parameter to avoid CSRF; rely on Flask's secret key for session signing.
- **Local development friction**: document loopback redirect usage and make localhost redirect configurable.

## Open Questions
- Should sign-in be limited to a specific Google Workspace domain, or is any Google account acceptable? (Assume “any account” unless clarified.)
- Do we need to capture/store email for audit records beyond a session? (Assume session-only storage for now.)
