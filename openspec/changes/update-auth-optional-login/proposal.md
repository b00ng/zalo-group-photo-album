# Make Google Login Optional

## Summary
- Allow visitors to use clustering, search, and timeline features without signing in.
- Keep Google OAuth available so users can identify themselves, but treat authentication as optional.
- Update UX copy so users understand login is optional and primarily for personalization or future features.

## Motivation
- Some environments cannot use Google accounts or prefer anonymous, local-only processing.
- Reduces setup friction by letting users skip credential configuration while exploring the app.

## Scope
- Adjust backend authentication guard to let anonymous sessions reach existing routes.
- Keep `/login`, `/auth/google`, `/logout`, and session handling available for optional sign-in.
- Update templates to hide login prompts when unnecessary and to clarify optional sign-in behavior.
- Update documentation to reflect the new optional sign-in flow.

## Out of Scope
- Adding alternative identity providers or roles.
- Persisting personalized settings for authenticated users.
- Any changes to clustering, search, or timeline algorithms beyond authentication gates.

## User Impact
- Users can immediately use the app after startup without configuring Google OAuth.
- Signed-in users still see their profile info and can sign out, but anonymous users see the same features.

## Dependencies / Tooling
- Existing Google OAuth libraries remain; no new dependencies.

## Risks & Mitigations
- **Residual Google config validation**: ensure startup no longer fails when credentials are absent.
- **Accidentally exposing private files**: keep filesystem safeguards intact when bypassing auth.

## Open Questions
- Should anonymous sessions suppress any user-specific messaging (e.g., welcome text)? Assume yes, keep UI neutral.
