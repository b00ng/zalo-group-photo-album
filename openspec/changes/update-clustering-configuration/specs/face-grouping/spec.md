## ADDED Requirements

### Requirement: Cluster detected faces for review
The system MUST compute face embeddings for every detected face, cluster them in a single pass, and return draft groups that represent unique people in the Review Gallery.
#### Scenario: Album contains multiple people
- Given the user starts cluster discovery for a folder with photos containing multiple faces
- When the system processes the folder
- Then it generates an embedding for each detected face using the configured InsightFace model
- And it clusters all embeddings together before rendering the Review Gallery
- And each resulting group lists the face thumbnails and ids assigned to that cluster

#### Scenario: No faces detected
- Given the user starts cluster discovery for a folder with no detectable faces
- When processing completes
- Then the system reports that no faces were found without creating any clusters

### Requirement: Provide tunable clustering controls
The cluster discovery flow MUST accept similarity (`eps`) and minimum sample (`min_samples`) parameters, applying user-supplied values when valid and defaulting to `eps = 0.5` and `min_samples = 2` otherwise.
#### Scenario: User accepts defaults
- Given the user leaves the tuning fields empty
- When they start cluster discovery
- Then the backend runs DBSCAN with `eps = 0.5` and `min_samples = 2`
- And the Review Gallery renders the resulting clusters

#### Scenario: User supplies custom values
- Given the user enters a positive decimal for similarity and an integer ≥ 2 for minimum samples
- When they start cluster discovery
- Then the backend validates the inputs
- And it runs DBSCAN using the supplied values in place of the defaults
- And the Review Gallery reflects the clustering produced by those parameters

#### Scenario: User supplies invalid values
- Given the user submits non-numeric or out-of-range values for either field
- When the server receives the cluster discovery request
- Then it rejects the inputs, surfaces a human-readable error, and does not start processing
