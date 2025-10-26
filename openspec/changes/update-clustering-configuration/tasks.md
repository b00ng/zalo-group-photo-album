1. [x] Add similarity (`eps`) and minimum samples inputs to `templates/index.html`, pre-populated with defaults and basic client-side hints.
2. [x] Accept and validate the new form fields in `/process`; surface errors for invalid numbers and pass the parsed values into clustering.
3. [x] Update `PhotoProcessor.cluster_faces` to honour a configurable `min_samples` argument while preserving InsightFace-friendly defaults.
4. [x] Refresh user-facing docs (e.g., README) with guidance on tuning clustering parameters.
5. [ ] Manually verify processing with default values and with custom thresholds (including invalid input handling) to ensure groups render in the Review Gallery.
