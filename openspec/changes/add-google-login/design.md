# Design: Google Account Login

## Overview
Introduce a Google OAuth 2.0 Authorization Code flow so users must authenticate before accessing the photo album tools. The Flask app will manage the OAuth handshake, store minimal user info in the session, and guard existing routes.

## Flow
1. **Entry point**: Anonymous users landing on `/` or `/search` are redirected to `/login`. `/login` renders a page with a “Continue with Google” button that hits `/auth/google`.
2. **Authorize**: `/auth/google` builds the Google authorization URL with scopes `openid email profile`, a generated `state`, and redirects the browser there while persisting `state` in the session.
3. **Callback**: Google redirects to `/auth/google/callback` with `code` and `state`. The backend validates the `state`, exchanges the code for tokens using Google's token endpoint, and validates the ID token payload.
4. **Session**: On success, the session stores `google_user` (subject, email, name, avatar URL) and marks `is_authenticated=True`. Access tokens are discarded after fetching the profile; refresh tokens are not stored.
5. **Redirect**: User returns to the originally requested URL (saved in session before redirecting) or `/`.
6. **Sign-out**: `/logout` clears the session and redirects to `/login`.

## Data & Configuration
- **Session keys**: `google_user` dictionary `{sub, email, name, picture}`; `oauth_state`; `post_login_redirect`.
- **Environment**: Expect `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` (defaults to `${APP_URL}/auth/google/callback` if absent). Fail fast with descriptive error when missing.
- **Dependencies**: Add `google-auth`, `google-auth-oauthlib`, and upgrade Flask session secret guidance if not already set.

## Route Guard Strategy
- Wrap existing routes (`/`, `/process`, `/search`, `/run_search`, `/save_albums`, static cache serving) with a decorator that checks `session.get("is_authenticated")`.
- Redirect unauthenticated requests to `/login`, persisting the original URL for post-login redirect.
- Ensure JSON endpoints (`/save_albums`) respond with `401` JSON payload if called via XHR without auth.

## Security Considerations
- Generate a cryptographically random `state` per login attempt to prevent CSRF attacks.
- Validate the ID token audience (`aud`) against `GOOGLE_CLIENT_ID` and the issuer (`iss`) against Google's domains.
- Limit OAuth scope to `openid email profile` to avoid extra consent prompts.
- Use HTTPS redirect URI in production; document that localhost development can use `http://localhost:8080/auth/google/callback`.

## Alternative Considerations
- Could use hosted Firebase Authentication, but it adds client-side SDK complexity and is unnecessary for a server-rendered Flask app.
- Rolling our own OAuth via `requests` is possible; using `google-auth-oauthlib` reduces surface for implementation mistakes.
