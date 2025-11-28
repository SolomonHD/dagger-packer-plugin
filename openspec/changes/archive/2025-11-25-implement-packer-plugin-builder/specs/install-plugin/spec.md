# Install Plugin Capability

## ADDED Requirements

### Requirement: Plugin Binary Input
The module SHALL accept a built plugin binary (from build-plugin output) as input for installation.

#### Scenario: Binary from build-plugin
- **WHEN** install_plugin receives a container with built binary at `/work/packer-plugin-{name}`
- **THEN** the module proceeds with installation

#### Scenario: Binary file directly provided
- **WHEN** caller provides a Dagger File containing the plugin binary
- **THEN** the module uses that file for installation

### Requirement: Git Source for Installation
The module SHALL use the git_source parameter to register the plugin with Packer.

#### Scenario: Plugin registration
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **AND** binary `packer-plugin-docker` is available
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/hashicorp/packer-plugin-docker`

### Requirement: Packer Container
The module SHALL execute plugin installation inside the official HashiCorp Packer container.

#### Scenario: Default Packer version
- **WHEN** packer_version parameter is not provided
- **THEN** the module uses `hashicorp/packer:latest` image

#### Scenario: Specific Packer version
- **WHEN** packer_version parameter is `1.10.0`
- **THEN** the module uses `hashicorp/packer:1.10.0` image

### Requirement: Installation Artifact Collection
The module SHALL collect all files from the Packer plugin installation directory.

#### Scenario: Successful installation
- **WHEN** `packer plugins install` completes successfully
- **THEN** the module copies all files from `~/.packer.d/plugins/{git_source_path}/`

#### Scenario: Installation output structure
- **WHEN** plugin is installed for `github.com/user/packer-plugin-example` version `1.0.0`
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