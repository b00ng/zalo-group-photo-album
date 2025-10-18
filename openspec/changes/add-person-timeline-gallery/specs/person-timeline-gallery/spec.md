## ADDED Requirements

### Requirement: Capture photo timestamps during face extraction
The system MUST record a timestamp for every detected face by reading the source photo’s EXIF `DateTimeOriginal` value when available and falling back to the file’s modification time.
#### Scenario: Photo contains EXIF timestamp
- Given a photo includes an EXIF `DateTimeOriginal`
- When faces are extracted from the photo
- Then each face record stored in the cache includes `taken_at` set to the parsed timestamp in ISO 8601 format
- And the timestamp represents the same moment as the EXIF value (converted to UTC if needed)

#### Scenario: Photo is missing EXIF timestamp
- Given a photo lacks an EXIF timestamp
- When faces are extracted from the photo
- Then `taken_at` is set using the filesystem modified time
- And the record indicates the timestamp source is `file_modified`

### Requirement: Persist cluster assignments for timeline lookup
The application MUST persist the latest cluster-to-face mapping in the cache so timeline routes can resolve the faces belonging to each person.
#### Scenario: Review gallery data is generated
- Given clustering completes and cluster UI data is generated
- When the system prepares cluster data for the review page
- Then it writes a cache file that maps each cluster id to the list of associated face ids and cluster names
- And the cache file is updated whenever clustering runs again

### Requirement: Provide timeline index route
The application MUST expose a `/timeline` route listing all current clusters with their display names and photo counts, restricted to authenticated users.
#### Scenario: Authenticated user visits /timeline
- Given the user is signed in
- When they navigate to `/timeline`
- Then they see a list of every available cluster/person with its name and total photo count
- And each entry links to `/timeline/<cluster_id>`

#### Scenario: Anonymous visitor requests /timeline
- Given a visitor is not authenticated
- When they navigate to `/timeline`
- Then they are redirected to the login page before any cluster information is shown

### Requirement: Render chronological timeline per person
The timeline view MUST present the selected person’s photos ordered by their recorded timestamps and grouped by day.
#### Scenario: Authenticated user views a person timeline
- Given the user is signed in
- And the selected cluster contains photos with timestamps derived from EXIF and/or file modification times
- When they navigate to `/timeline/<cluster_id>`
- Then the page shows the cluster name, total photo count, and the first-to-last timestamp range
- And photos are grouped under day headings sorted ascending by time within each group
- And each photo thumbnail links to a full-size version of the original image

#### Scenario: Timeline lacks timestamps
- Given every photo in a cluster has no timestamp information
- When the user views `/timeline/<cluster_id>`
- Then the page indicates the dates are unknown but still lists the photos in a deterministic order (e.g., by filename)

### Requirement: Secure photo delivery for timeline view
The application MUST ensure that any route used to render or download original photos for the timeline only serves files from whitelisted directories and rejects traversal attempts.
#### Scenario: Timeline requests a photo outside allowed directories
- Given the timeline requests to load an image path outside the configured photo roots
- When the backend resolves the request
- Then it returns HTTP 403 without reading the file

#### Scenario: Timeline requests a valid photo
- Given an image path belongs to the cached photo set for a cluster
- When the backend serves the image
- Then it returns the original photo content with the correct MIME type
