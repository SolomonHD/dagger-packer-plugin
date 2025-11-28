## MODIFIED Requirements

### Requirement: Containerized Build
The module SHALL execute the Go build inside a container using the official Go image. When determining the Go version, the module SHALL use a priority-based resolution: explicit `go_version` parameter takes precedence over `.go-version` file detection, which takes precedence over the default fallback.

#### Scenario: Explicit go_version parameter provided
- **WHEN** go_version parameter is `1.22`
- **THEN** the module uses the `golang:1.22` container image
- **AND** ignores any `.go-version` file in the source directory

#### Scenario: No go_version parameter and .go-version file exists
- **WHEN** go_version parameter is not provided
- **AND** source directory contains a `.go-version` file with content `1.23.2`
- **THEN** the module reads the file, strips whitespace, and uses `golang:1.23.2` container image

#### Scenario: No go_version parameter and no .go-version file
- **WHEN** go_version parameter is not provided
- **AND** source directory does not contain a `.go-version` file
- **THEN** the module uses Go 1.21 as the default fallback

#### Scenario: .go-version file with trailing newline
- **WHEN** source directory contains `.go-version` file with content `1.23.2\n`
- **AND** go_version parameter is not provided
- **THEN** the module strips the trailing newline and uses `golang:1.23.2` container image

## ADDED Requirements

### Requirement: Cache-Busting for Binary Export
The module SHALL invalidate Dagger's layer cache for build operations to ensure binary and checksum files are always exported on every run.

#### Scenario: Repeated build exports binary
- **WHEN** user runs `build-and-install` with identical parameters
- **AND** a previous run has already completed successfully
- **THEN** the binary and checksum files are still exported to the output path

#### Scenario: Cache invalidation mechanism
- **WHEN** building the plugin
- **THEN** the module injects a cache-busting environment variable (e.g., timestamp or UUID) into the build container
- **AND** this ensures Dagger re-executes the export step