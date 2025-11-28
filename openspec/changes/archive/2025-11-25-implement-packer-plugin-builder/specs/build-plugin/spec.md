# Build Plugin Capability

## ADDED Requirements

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
The module SHALL build the plugin using Go with ldflags that clear the VersionPrerelease variable.

#### Scenario: Standard build
- **WHEN** building plugin with git_source `github.com/user/packer-plugin-example`
- **THEN** the module executes Go build with `-ldflags="-X github.com/user/packer-plugin-example/version.VersionPrerelease="`

#### Scenario: Build output naming
- **WHEN** plugin name is `docker`
- **THEN** the output binary is named `packer-plugin-docker` (no `-dev` suffix)

### Requirement: Containerized Build
The module SHALL execute the Go build inside a container using the official Go image.

#### Scenario: Default Go version
- **WHEN** go_version parameter is not provided
- **THEN** the module uses Go 1.21 or later stable version

#### Scenario: Custom Go version
- **WHEN** go_version parameter is `1.22`
- **THEN** the module uses the `golang:1.22` container image

### Requirement: Build Output
The module SHALL return a Dagger Container containing the built plugin binary.

#### Scenario: Successful build
- **WHEN** Go build completes successfully
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions

#### Scenario: Build failure
- **WHEN** Go build fails (compilation errors)
- **THEN** the module surfaces the build error with Go compiler output