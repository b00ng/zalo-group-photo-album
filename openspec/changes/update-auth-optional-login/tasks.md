## 1. Implementation
- [x] 1.1 Relax authentication guard so protected routes allow anonymous access while still supporting optional login sessions.
- [x] 1.2 Make Google OAuth startup optional (skip hard failure when credentials missing) and adjust related config messaging.
- [x] 1.3 Update templates/navigation to reflect optional sign-in: show login prompts when available and neutral copy otherwise.
- [x] 1.4 Ensure timeline/photo-serving security checks remain intact for anonymous users.
- [x] 1.5 Update README (or other docs) to document the optional login flow.

## 2. Validation
- [ ] 2.1 Manually verify anonymous access works across clustering, search, timeline, and export flows.
- [ ] 2.2 Verify optional login still functions end-to-end when credentials are provided.
