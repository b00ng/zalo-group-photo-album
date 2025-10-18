# Design: Timeline Galleries Per Person

## Overview
Enable a chronological gallery for each identified person by capturing capture timestamps during face extraction, persisting them in the cache, and adding a new view that orders the person's photos by those timestamps.

## Data Flow
1. **Face extraction**: When `PhotoProcessor.extract_faces` processes an image, it will:
   - Attempt to read `DateTimeOriginal` (or similar) via Pillow's EXIF helpers.
   - Convert the value to an ISO 8601 string (assume UTC) and store it as `taken_at` for each face record.
   - Fall back to the file's modification time when EXIF is missing.
2. **Cache persistence**: Extend `all_faces_data.json` entries with `taken_at` and a `thumbnail_url` for quick access.
3. **Cluster metadata**: Persist the latest cluster assignments in a new cache file (e.g., `cluster_assignments.json`) when generating the gallery data so runtime routes can map a person id to their face ids.

## Timeline Route
- Add Flask route `/timeline/<int:cluster_id>` that:
  - Validates the requester is authenticated.
  - Loads cached faces and cluster assignments.
  - Determines the distinct source photos for the selected cluster and groups them by day (YYYY-MM-DD) while keeping chronological order.
  - Returns a template-rendered page with sections per day, each containing thumbnails linking to the original files (served via a new static-serving endpoint if needed).
- Provide an index endpoint `/timeline` that lists available clusters with their current names so users can jump directly to one.

## UI
- In the existing review gallery, add a "View timeline" affordance on each cluster card that opens `/timeline/<cluster_id>`.
- Timeline template displays:
  - Cluster name, total photo count, date range.
  - Day buckets with thumbnails and relative time labels.
  - Optional lazy loading via simple IntersectionObserver or "Load more" button (keep minimal: render all for now while keeping thumbnails small).

## Serving Original Photos
- To avoid leaking arbitrary filesystem paths, add a secure route (e.g., `/photos/<path:filename>`) that reads from whitelisted processed directories. The timeline will reference this route for full-size image downloads while thumbnails can be generated on the fly (using cached face crops) or rely on resized versions stored in a new `thumbnails` cache.
- Minimal approach: reuse cached face crops for thumbnails and provide a link to the album copy if already exported.

## Security & Privacy
- Reuse existing login/session guard so that timeline routes require authentication.
- Ensure the new photo-serving route validates paths reside under the configured base directory to avoid directory traversal.

## Dependencies
- Add `Pillow` to `requirements.txt` for EXIF extraction.
- Consider simple `dateutil` parsing if EXIF values vary; if not, implement manual parsing to avoid extra dependencies.
