## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Go Build with Ldflags
The module SHALL build the plugin using Go with ldflags that clear the VersionPrerelease variable, using the normalized lowercase git_source.

#### Scenario: Standard build with uppercase input
- **WHEN** building plugin with git_source `github.com/SolomonHD/packer-plugin-Example`
- **THEN** the module normalizes to lowercase
- **AND** executes Go build with `-ldflags="-X github.com/solomonhd/packer-plugin-example/version.VersionPrerelease="`

#### Scenario: Build output naming
- **WHEN** plugin name is `Docker` (uppercase)
- **THEN** the output binary is named `packer-plugin-docker` (lowercase, no `-dev` suffix)