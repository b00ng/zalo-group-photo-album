1. [x] Add Pillow dependency and helper utilities for reading EXIF timestamps with fallback to filesystem metadata.
2. [x] Extend `PhotoProcessor` to capture `taken_at` plus timestamp source per face and persist the data in `all_faces_data.json`.
3. [x] Persist cluster assignments (cluster id, name, face ids) in a cache file whenever cluster UI data is generated.
4. [x] Implement authenticated `/timeline` and `/timeline/<cluster_id>` routes plus a secure photo-serving endpoint limited to cached/album directories.
5. [x] Build timeline templates/components showing cluster metadata, day groupings, thumbnails, and navigation from the review gallery.
6. [ ] Update documentation with timeline usage notes and run manual verification covering EXIF parsing fallbacks, auth protection, and secure file serving. (Documentation updated; manual verification requires real photo set.)
