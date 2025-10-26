## Why
- Some operators prefer running clustering pipelines directly from the command line without running the Flask UI.
- Documenting a CLI workflow helps teams automate batch jobs or remotely trigger face grouping without browsers.
- Without guidance, users must infer which scripts and parameters to call, risking misconfiguration.

## What Changes
- Introduce documentation detailing how to execute cluster discovery (face extraction, clustering, and album export) via a command-line entry point or Python module.
- Provide example commands, expected inputs/outputs, and environment preparation so users can follow the steps without the web app.
- Highlight how to supply clustering parameters and where results are written.

## Impact
- Improves usability for automation scenarios or headless environments.
- No code changes required; only documentation updates.
- Clarifies how existing modules can be reused outside Flask.
