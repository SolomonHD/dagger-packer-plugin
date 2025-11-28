# version-detection Specification

## Purpose
TBD - created by archiving change implement-packer-plugin-builder. Update Purpose after archive.
## Requirements
### Requirement: Version Source Detection
The module SHALL analyze plugin source code to detect how version information is managed.

#### Scenario: Detect embed pattern with VERSION file
- **WHEN** source contains `version/version.go` with `//go:embed VERSION`
- **AND** `version/VERSION` file exists
- **THEN** detection reports `version_source: "file"` and `version_file: "version/VERSION"`

#### Scenario: Detect root VERSION file
- **WHEN** source contains `VERSION` file at repository root
- **AND** Go code references this file (via embed or build)
- **THEN** detection reports `version_source: "file"` and `version_file: "VERSION"`

#### Scenario: Detect hardcoded version
- **WHEN** source contains `var Version = "1.0.0"` pattern in Go code
- **AND** no VERSION file exists
- **THEN** detection reports `version_source: "hardcoded"` and `hardcoded_value: "1.0.0"`

#### Scenario: Detect ldflags pattern
- **WHEN** source version.go contains `var Version string` without initialization
- **THEN** detection reports `version_source: "ldflags"` (expects -X flag at build time)

### Requirement: Use VERSION File Option
The module SHALL provide a `use_version_file` flag to use the embedded VERSION file instead of explicit version parameter.

#### Scenario: Use VERSION file as authoritative
- **WHEN** `use_version_file` is `true`
- **AND** detection found VERSION file at `version/VERSION` containing `1.2.3`
- **THEN** the build uses `1.2.3` as version without requiring explicit `--version` parameter

#### Scenario: VERSION file not found with flag enabled
- **WHEN** `use_version_file` is `true`
- **AND** no VERSION file is detected
- **THEN** the module returns an error indicating no VERSION file found

#### Scenario: Explicit version overrides file
- **WHEN** both `use_version_file` is `true` and `--version=2.0.0` is provided
- **THEN** the explicit `--version` parameter takes precedence and uses `2.0.0`

### Requirement: Version File Update
The module SHALL optionally update the VERSION file before build when an explicit version is provided.

#### Scenario: Update VERSION file for embedded version
- **WHEN** explicit `--version=2.0.0` is provided
- **AND** `update_version_file` is `true`
- **AND** VERSION file exists at detected path
- **THEN** the VERSION file is updated to contain `2.0.0` before Go build

#### Scenario: Preserve VERSION file by default
- **WHEN** explicit `--version=2.0.0` is provided
- **AND** `update_version_file` is not set or `false`
- **THEN** the VERSION file remains unchanged (ldflags still override at build time)

### Requirement: Hardcoded Version Override
The module SHALL override hardcoded versions using Go ldflags.

#### Scenario: Override hardcoded version via ldflags
- **WHEN** plugin has hardcoded `var Version = "1.0.0"`
- **AND** explicit `--version=2.0.0` is provided
- **THEN** build includes `-ldflags="-X {git_source}/version.Version=2.0.0"`

#### Scenario: Override both Version and VersionPrerelease
- **WHEN** building with explicit version
- **THEN** ldflags includes both `-X .../version.Version={version}` AND `-X .../version.VersionPrerelease=`

### Requirement: Version Detection Report
The module SHALL provide a function to report detected version configuration.

#### Scenario: Detection report output
- **WHEN** caller invokes `detect_version()` with source directory
- **THEN** the module returns JSON report including:
  - `version_source`: one of `file`, `hardcoded`, `ldflags`
  - `version_file`: path if applicable
  - `current_version`: detected value if applicable
  - `version_package`: detected package path (e.g., `github.com/user/plugin/version`)

#### Scenario: Detection with recommendation
- **WHEN** detection finds embed pattern with VERSION file
- **THEN** report includes `recommendation: "use_version_file"` indicating cleanest approach

### Requirement: Version Validation
The module SHALL validate version format before build.

#### Scenario: Valid semantic version
- **WHEN** version is `1.0.0`, `2.3.4`, or `0.1.0-beta.1`
- **THEN** validation passes

#### Scenario: Invalid version format
- **WHEN** version is `v1.0.0` (with v prefix) or `1.0` (incomplete)
- **THEN** the module returns error with guidance on proper format

#### Scenario: Version mismatch warning
- **WHEN** VERSION file contains `1.0.0`
- **AND** explicit `--version=2.0.0` is provided
- **AND** `update_version_file` is `false`
- **THEN** the module emits warning about potential version mismatch in embedded vs built binary

