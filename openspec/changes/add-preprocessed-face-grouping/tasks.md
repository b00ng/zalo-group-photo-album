1. [x] Add a navigation link and template/form that collects an original photo folder path and a faces cache folder path for the reuse flow.
2. [x] Implement backend handling that validates inputs, loads embeddings/metadata from the cache, clusters faces, and copies grouped photos into a fresh output subdirectory.
3. [x] Report success or validation errors to the user, including the path of the generated grouped albums.
4. [x] Update documentation with instructions for using cached faces (expected directory layout, when to use the feature).
5. [ ] Manually verify the flow with an existing `.cache` directory (success), a missing `all_faces_data.json` (error), and mismatched photo paths.
