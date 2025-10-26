## Why
- Teams sometimes already have cropped face datasets from earlier processing but need to rebuild grouped photo albums without re-running detection.
- Re-extracting embeddings and crops from the original photos adds time and requires the raw images to be reprocessed, even when the cache already exists.
- Providing a reuse path lets operators point at an existing faces cache plus the photo directory and produce grouped albums directly.

## What Changes
- Add a new "Group Existing Faces" flow that accepts (a) the original photos directory and (b) a directory containing cached faces/embeddings (e.g., `all_faces_data.json` and crops).
- Load embeddings and original photo references from the cache, cluster them, and immediately materialize per-person subfolders inside the configured output directory.
- Validate that the cache directory contains the required metadata, reject invalid inputs with clear errors, and report the output path back to the user.
- Document the new flow so users know how to structure the cache and when to choose it over full reprocessing.

## Impact
- Saves time for large albums when the face cache is already available.
- Avoids duplicate face extraction work while reusing the same clustering logic.
- Slight increase in UI/route surface; no changes to InsightFace model usage.
