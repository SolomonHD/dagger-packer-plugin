## MODIFIED Requirements

### Requirement: Git Source Path
The module SHALL accept an optional git source path parameter named `git_source` representing the plugin's canonical import path. When not provided, the module SHALL auto-detect it from the `go.mod` file in the source directory.

#### Scenario: Explicit GitHub path provided
- **WHEN** git_source is explicitly set to `github.com/hashicorp/packer-plugin-docker`
- **THEN** the module uses this path for ldflags and output naming
- **AND** auto-detection from go.mod is skipped

#### Scenario: Private git server path provided
- **WHEN** git_source is explicitly set to `git.internal.company.com/team/packer-plugin-custom`
- **THEN** the module uses this path without modification
- **AND** auto-detection from go.mod is skipped

#### Scenario: git_source not provided and go.mod exists
- **WHEN** git_source parameter is not provided
- **AND** source directory contains a valid `go.mod` file with module declaration
- **THEN** the module parses the `module` directive from go.mod
- **AND** uses the extracted module path as git_source
- **AND** outputs informational message: `ℹ Using git-source from go.mod: <path>`

#### Scenario: git_source not provided and go.mod missing
- **WHEN** git_source parameter is not provided
- **AND** source directory does not contain a `go.mod` file
- **THEN** the module returns an error: `✗ Error: --git-source required (could not auto-detect from go.mod: file not found)`

#### Scenario: git_source not provided and go.mod unparseable
- **WHEN** git_source parameter is not provided
- **AND** source directory contains a `go.mod` file without a valid module declaration
- **THEN** the module returns an error: `✗ Error: --git-source required (could not auto-detect from go.mod: no module declaration found)`

## ADDED Requirements

### Requirement: Auto-Detected Git Source Normalization
The module SHALL apply the same lowercase normalization to auto-detected git_source values as applied to explicitly provided values.

#### Scenario: Auto-detected git_source normalized to lowercase
- **WHEN** git_source is auto-detected from go.mod as `github.com/SolomonHD/packer-plugin-Example`
- **THEN** the module normalizes to `github.com/solomonhd/packer-plugin-example`
- **AND** outputs warning: `⚠ Warning: git-source normalized to lowercase: github.com/solomonhd/packer-plugin-example`
- **AND** outputs info: `ℹ Using git-source from go.mod: github.com/solomonhd/packer-plugin-example`

#### Scenario: Auto-detected git_source already lowercase
- **WHEN** git_source is auto-detected from go.mod as `github.com/hashicorp/packer-plugin-docker`
- **THEN** the module uses the path without modification
- **AND** no normalization warning is output
- **AND** outputs info: `ℹ Using git-source from go.mod: github.com/hashicorp/packer-plugin-docker`