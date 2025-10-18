# Add Timeline Galleries Per Person

## Summary
- Extend the app so every identified person has a dedicated, chronological photo gallery.
- Capture shot timestamps during clustering and expose a timeline view that orders the person's photos by when they were taken.

## Motivation
- Storytelling, memory recall, and debugging mislabeled faces are easier when photos are shown in time order instead of an arbitrary cluster list.
- A per-person timeline keeps the UI focused while avoiding manual sorting in exported folders.

## Scope
- Extract capture timestamps per face/photo (prefer EXIF `DateTimeOriginal`, fall back to filesystem modified time) during face processing.
- Persist timestamps with existing cache data so later routes can render them.
- Provide backend routes and templates/JS to render a timeline gallery per cluster/person, reachable from the review experience.
- Add lightweight navigation from the review gallery to each person's timeline.

## Out of Scope
- Video timeline support or cross-person comparisons.
- Advanced filtering (e.g., by location, tags) or bulk editing within the timeline.
- Editing EXIF metadata or rewriting original files with new timestamps.

## User Impact
- Reviewers can click from a person's cluster to see their photos ordered by time, with dates displayed.
- Exported albums remain as-is; timeline is a web experience only.

## Dependencies / Tooling
- Likely need `Pillow` (or similar) for robust EXIF parsing.
- Minor CSS/JS additions for the timeline layout.

## Risks & Mitigations
- **Missing EXIF data:** fall back to file modified times and label them as "Unknown date" when unavailable.
- **Performance** when loading large albums: lazy-load thumbnails and reuse cached face crops to avoid reading full images repeatedly.
- **Timezone ambiguity:** store naive timestamps in UTC based on EXIF or filesystem, and display formatted local date strings.

## Open Questions
- Should the timeline group photos by day/month or remain a flat chronological list? (Assume day grouping buckets for now.)
- Do we need deep links/bookmarks for a specific date range within a person's timeline?
