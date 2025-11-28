# install-plugin Specification

## Purpose
TBD - created by archiving change implement-packer-plugin-builder. Update Purpose after archive.
## Requirements
### Requirement: Plugin Binary Input
The module SHALL accept a built plugin binary (from build-plugin output) as input for installation.

#### Scenario: Binary from build-plugin
- **WHEN** install_plugin receives a container with built binary at `/work/packer-plugin-{name}`
- **THEN** the module proceeds with installation

#### Scenario: Binary file directly provided
- **WHEN** caller provides a Dagger File containing the plugin binary
- **THEN** the module uses that file for installation

### Requirement: Git Source for Installation
The module SHALL use the normalized lowercase git_source parameter to register the plugin with Packer.

#### Scenario: Plugin registration with uppercase input
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Docker`
- **AND** binary `packer-plugin-docker` is available
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/solomonhd/packer-plugin-docker`

### Requirement: Packer Container
The module SHALL execute plugin installation inside the official HashiCorp Packer container.

#### Scenario: Default Packer version
- **WHEN** packer_version parameter is not provided
- **THEN** the module uses `hashicorp/packer:latest` image

#### Scenario: Specific Packer version
- **WHEN** packer_version parameter is `1.10.0`
- **THEN** the module uses `hashicorp/packer:1.10.0` image

### Requirement: Installation Artifact Collection
The module SHALL collect all files from the Packer plugin installation directory using the transformed git_source path.

#### Scenario: Successful installation
- **WHEN** `packer plugins install` completes successfully
- **AND** git_source was `github.com/user/packer-plugin-example`
- **THEN** the module copies all files from `~/.packer.d/plugins/github.com/user/example/`

#### Scenario: Installation output structure
- **WHEN** plugin is installed for original git_source `github.com/user/packer-plugin-example` version `1.0.0`
- **THEN** output directory contains:
  - `packer-plugin-example_v1.0.0_x5.0_{os}_{arch}` (binary)
  - `packer-plugin-example_v1.0.0_x5.0_{os}_{arch}_SHA256SUM` (checksum)

### Requirement: Installation Output
The module SHALL return a Dagger Directory containing the installation artifacts.

#### Scenario: Directory export
- **WHEN** installation completes successfully
- **THEN** the returned Directory can be exported to the caller's filesystem via `.export()`

#### Scenario: Installation failure
- **WHEN** `packer plugins install` fails
- **THEN** the module surfaces the Packer error output

### Requirement: Build and Install Workflow
The module SHALL provide a composite function that combines build and install phases.

#### Scenario: Single command workflow
- **WHEN** caller invokes `build_and_install()` with source, git_source, and version
- **THEN** the module builds the plugin, installs it, and returns installation artifacts

#### Scenario: Workflow export
- **WHEN** caller chains `.export(path=".")` to `build_and_install()` output
- **THEN** installation files are exported to the specified directory

### Requirement: Plugin Source Path Transformation
The module SHALL transform the git_source parameter by stripping the `packer-plugin-` prefix from the final path segment when constructing the source string for `packer plugins install` command.

#### Scenario: Standard packer-plugin prefix
- **WHEN** git_source is `github.com/solomonhd/packer-plugin-ansible-navigator`
- **THEN** the install command receives source `github.com/solomonhd/ansible-navigator`
- **AND** plugin path retrieval uses `github.com/solomonhd/ansible-navigator`

#### Scenario: Different git hosting with packer-plugin prefix
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **THEN** the install command receives source `github.com/hashicorp/docker`
- **AND** plugin path retrieval uses `github.com/hashicorp/docker`

#### Scenario: Git source without packer-plugin prefix
- **WHEN** git_source is `github.com/user/custom-plugin` (no packer-plugin- prefix)
- **THEN** the install command receives source unchanged as `github.com/user/custom-plugin`
- **AND** plugin path retrieval uses `github.com/user/custom-plugin`

#### Scenario: Prefix appears only in final segment
- **WHEN** git_source is `git.company.com/packer-plugins/packer-plugin-custom`
- **THEN** only the final segment is transformed: `git.company.com/packer-plugins/custom`
- **AND** intermediate path segments containing "packer-plugin" are preserved

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

