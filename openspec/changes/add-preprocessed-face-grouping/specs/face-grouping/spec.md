## ADDED Requirements

### Requirement: Reuse cached faces for clustering
The system MUST allow users to group people using a previously generated faces cache without re-running face detection.
#### Scenario: Valid cache provided
- Given the user supplies a folder containing the original photos
- And they provide a faces cache directory that includes `all_faces_data.json` with embeddings and photo references
- When they run the reuse flow
- Then the system loads the cached embeddings, performs clustering, and creates one subfolder per cluster inside the output directory
- And each subfolder contains every original photo associated with that cluster

### Requirement: Validate reuse inputs
The reuse flow MUST validate inputs and refuse to run when the cache is incomplete or points at unavailable photos.
#### Scenario: Cache metadata missing
- Given the faces directory does not contain `all_faces_data.json`
- When the user submits the form
- Then the system returns an error explaining that the cache metadata is missing and no clustering is performed

#### Scenario: Photo reference outside provided directory
- Given the cache references an original photo path that is not located under the supplied photos directory
- When the flow runs
- Then the system stops processing, reports the mismatch, and does not copy any photos

### Requirement: Surface reuse results
The system MUST inform the user where the grouped albums were written and how many clusters were created.
#### Scenario: Reuse completes successfully
- Given clustering from cached faces succeeds
- When the system finishes copying grouped albums
- Then it shows a confirmation message containing the absolute output directory and the number of clusters created
