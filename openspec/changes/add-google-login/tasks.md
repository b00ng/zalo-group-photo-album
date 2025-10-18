1. [x] Add Google OAuth dependencies and configuration placeholders (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`) with startup validation.
2. [x] Implement `/login`, `/auth/google`, `/auth/google/callback`, and `/logout` routes plus session helpers for Google sign-in.
3. [x] Guard existing HTML and JSON endpoints with an authentication decorator that redirects or returns 401 appropriately.
4. [x] Update templates to add the login page, display signed-in user info, and expose a sign-out control.
5. [ ] Manually verify the OAuth flow end-to-end using Google test credentials (including failure cases) and document steps in the README. (Pending Google credentials; verification checklist documented in README.)
