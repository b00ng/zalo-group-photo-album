## ADDED Requirements

### Requirement: Document CLI cluster discovery workflow
The project MUST include documentation describing how to run the face extraction and clustering workflow from the command line without starting the Flask server.
#### Scenario: Operator wants to process an album via CLI
- Given a user reads the documentation
- When they follow the documented steps
- Then they can install dependencies, invoke the Python entry point, and generate grouped photo folders using only the command line
- And the documentation explains how to adjust clustering parameters and where outputs are written
