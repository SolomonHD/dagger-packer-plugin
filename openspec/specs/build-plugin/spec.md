# build-plugin Specification

## Purpose
TBD - created by archiving change implement-packer-plugin-builder. Update Purpose after archive.
## Requirements
### Requirement: Plugin Source Input
The module SHALL accept a Dagger Directory containing Packer plugin Go source code as a required parameter named `source`.

#### Scenario: Source directory provided
- **WHEN** caller provides a source directory via `--source` parameter
- **THEN** the module uses that directory as the build context

#### Scenario: Source directory omitted
- **WHEN** caller does not provide a source directory
- **THEN** the module returns an error indicating `--source` is required

### Requirement: Git Source Path
The module SHALL accept a git source path as a required parameter named `git_source` representing the plugin's canonical import path.

#### Scenario: GitHub path provided
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **THEN** the module uses this path for ldflags and output naming

#### Scenario: Private git server path
- **WHEN** git_source is `git.internal.company.com/team/packer-plugin-custom`
- **THEN** the module uses this path without modification

### Requirement: Version Parameter
The module SHALL accept a semantic version string as a required parameter named `version`.

#### Scenario: Valid semver provided
- **WHEN** version is `1.0.10`
- **THEN** the module uses this version in the build process

### Requirement: Plugin Name Auto-Detection
The module SHALL auto-detect the plugin name from the source directory name when `plugin_name` parameter is not provided.

#### Scenario: Standard packer-plugin directory name
- **WHEN** source directory is named `packer-plugin-docker`
- **AND** plugin_name parameter is not provided
- **THEN** the module extracts plugin name as `docker`

#### Scenario: Non-standard directory name
- **WHEN** source directory is named `my-custom-plugin`
- **AND** plugin_name parameter is not provided
- **THEN** the module uses `my-custom-plugin` as the plugin name

#### Scenario: Explicit plugin name override
- **WHEN** plugin_name parameter is `custom-name`
- **THEN** the module uses `custom-name` regardless of directory name

### Requirement: Go Build with Ldflags
The module SHALL build the plugin using Go with ldflags that clear the VersionPrerelease variable, using the normalized lowercase git_source.

#### Scenario: Standard build with uppercase input
- **WHEN** building plugin with git_source `github.com/SolomonHD/packer-plugin-Example`
- **THEN** the module normalizes to lowercase
- **AND** executes Go build with `-ldflags="-X github.com/solomonhd/packer-plugin-example/version.VersionPrerelease="`

#### Scenario: Build output naming
- **WHEN** plugin name is `Docker` (uppercase)
- **THEN** the output binary is named `packer-plugin-docker` (lowercase, no `-dev` suffix)

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

### Requirement: Build Output
The module SHALL return a Dagger Container containing the built plugin binary.

#### Scenario: Successful build
- **WHEN** Go build completes successfully
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions

#### Scenario: Build failure
- **WHEN** Go build fails (compilation errors)
- **THEN** the module surfaces the build error with Go compiler output

### Requirement: Git Source Lowercase Normalization
The module SHALL normalize the `git_source` parameter to lowercase before use in ldflags and output naming.

#### Scenario: Uppercase git source is normalized
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Docker`
- **THEN** the module uses `github.com/solomonhd/packer-plugin-docker` for ldflags
- **AND** outputs warning: `⚠ Warning: git-source normalized to lowercase: github.com/solomonhd/packer-plugin-docker`

#### Scenario: Lowercase git source unchanged
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **THEN** the module uses the path without modification
- **AND** no warning is output

### Requirement: Plugin Name Lowercase Normalization
The module SHALL normalize the `plugin_name` parameter (auto-detected or provided) to lowercase before use in binary naming.

#### Scenario: Uppercase plugin name is normalized
- **WHEN** plugin_name is `Docker` (explicit or auto-detected)
- **THEN** the module normalizes to `docker`
- **AND** outputs warning: `⚠ Warning: plugin-name normalized to lowercase: docker`
- **AND** binary name is `packer-plugin-docker`

#### Scenario: Lowercase plugin name unchanged
- **WHEN** plugin_name is `docker`
- **THEN** the module uses the name without modification
- **AND** no warning is output

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

