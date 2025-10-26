## Why
- Review Gallery clustering currently hardcodes DBSCAN parameters, which makes the grouping brittle for albums with different lighting, pose variance, or crowd density.
- Allowing operators to adjust similarity and minimum sample parameters lets them tighten or loosen grouping without editing code while keeping defaults aligned with today's behaviour.

## What Changes
- Add UI controls on the cluster discovery form to supply DBSCAN similarity (`eps`) and minimum sample (`min_samples`) values alongside the photo folder path.
- Propagate those values through the `/process` handler into `PhotoProcessor.cluster_faces`, falling back to the current InsightFace-friendly defaults when the user leaves them empty.
- Guard the inputs with simple validation (positive floats/integers) and show a friendly error when invalid values are provided.
- Document the new controls so reviewers understand how to tune grouping.

## Impact
- Users can adapt clustering behaviour per dataset without redeploying code.
- Minimal surface area change: same InsightFace pipeline, just exposes parameters.
- Slightly larger request payload when processing, no expected performance regressions.
