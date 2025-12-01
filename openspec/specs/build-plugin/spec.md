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
The module SHALL return a Dagger Container containing the built plugin binary. This function is intended for intermediate/development use when only the compiled binary is needed.

#### Scenario: Successful build
- **WHEN** Go build completes successfully via `build-binary` function
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions

#### Scenario: Build failure
- **WHEN** Go build fails (compilation errors) during `build-binary` execution
- **THEN** the module surfaces the build error with Go compiler output

#### Scenario: Intermediate development workflow
- **WHEN** developer needs to test binary compilation without creating complete artifacts
- **THEN** `build-binary` provides the compiled binary in a container for inspection or testing

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

### Requirement: Target Operating System
The module SHALL accept an optional `target_os` parameter specifying the target operating system for cross-compilation.

#### Scenario: Default target OS when not provided
- **WHEN** `target_os` parameter is not provided
- **THEN** the module defaults to `linux`
- **AND** the Go build runs with `GOOS=linux` environment variable

#### Scenario: Explicit target OS provided
- **WHEN** `target_os` parameter is `darwin`
- **THEN** the Go build runs with `GOOS=darwin` environment variable

#### Scenario: Windows target OS
- **WHEN** `target_os` parameter is `windows`
- **THEN** the Go build runs with `GOOS=windows` environment variable
- **AND** the output binary has `.exe` extension

### Requirement: Target Architecture
The module SHALL accept an optional `target_arch` parameter specifying the target CPU architecture for cross-compilation.

#### Scenario: Default target architecture when not provided
- **WHEN** `target_arch` parameter is not provided
- **THEN** the module defaults to `amd64`
- **AND** the Go build runs with `GOARCH=amd64` environment variable

#### Scenario: ARM64 target architecture
- **WHEN** `target_arch` parameter is `arm64`
- **THEN** the Go build runs with `GOARCH=arm64` environment variable

#### Scenario: 386 target architecture
- **WHEN** `target_arch` parameter is `386`
- **THEN** the Go build runs with `GOARCH=386` environment variable

### Requirement: Cross-Compilation Environment
The module SHALL set `GOOS`, `GOARCH`, and `CGO_ENABLED=0` environment variables during the Go build process.

#### Scenario: Full cross-compilation environment
- **WHEN** building with `target_os=darwin` and `target_arch=arm64`
- **THEN** the Go build container has environment variables:
  - `GOOS=darwin`
  - `GOARCH=arm64`
  - `CGO_ENABLED=0`

#### Scenario: Default cross-compilation environment
- **WHEN** building without specifying `target_os` or `target_arch`
- **THEN** the Go build container has environment variables:
  - `GOOS=linux`
  - `GOARCH=amd64`
  - `CGO_ENABLED=0`

### Requirement: Function Purpose Documentation
The `build_binary` function SHALL be documented as an intermediate/development tool for compiling the raw Go binary, while `build_artifacts` (in install-plugin spec) is the recommended workflow for production use.

#### Scenario: Usage guidance in docstring
- **WHEN** user invokes `dagger functions` or reads function help
- **THEN** the `build-binary` docstring clearly indicates it builds only the binary
- **AND** recommends using `build-artifacts` for production-ready plugin packages

#### Scenario: README documentation structure
- **WHEN** user reads the README
- **THEN** primary examples feature `build-artifacts` workflow
- **AND** `build-binary` examples appear in "Advanced" or "Build Binary Only" section
- **AND** context explains when to use each function

