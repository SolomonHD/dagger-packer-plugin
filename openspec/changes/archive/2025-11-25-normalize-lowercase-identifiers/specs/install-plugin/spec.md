## ADDED Requirements

### Requirement: Git Source Lowercase Normalization for Installation
The module SHALL normalize the `git_source` parameter to lowercase before use in plugin registration and path construction.

#### Scenario: Uppercase git source is normalized during registration
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Docker`
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/solomonhd/packer-plugin-docker`
- **AND** outputs warning: `⚠ Warning: git-source normalized to lowercase: github.com/solomonhd/packer-plugin-docker`

#### Scenario: Plugin path uses normalized git source
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Example`
- **THEN** the plugin path is `/root/.packer.d/plugins/github.com/solomonhd/packer-plugin-example`

#### Scenario: Lowercase git source unchanged
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **THEN** the module uses the path without modification
- **AND** no warning is output

### Requirement: Plugin Name Lowercase Normalization for Installation
The module SHALL normalize the `plugin_name` parameter (auto-detected or provided) to lowercase before use in binary name references.

#### Scenario: Uppercase plugin name normalized for binary reference
- **WHEN** plugin_name is `Docker`
- **THEN** the module references binary as `packer-plugin-docker`
- **AND** outputs warning: `⚠ Warning: plugin-name normalized to lowercase: docker`

#### Scenario: Lowercase plugin name unchanged
- **WHEN** plugin_name is `docker`
- **THEN** the module uses the name without modification
- **AND** no warning is output

## MODIFIED Requirements

### Requirement: Git Source for Installation
The module SHALL use the normalized lowercase git_source parameter to register the plugin with Packer.

#### Scenario: Plugin registration with uppercase input
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Docker`
- **AND** binary `packer-plugin-docker` is available
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/solomonhd/packer-plugin-docker`