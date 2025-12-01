# install-plugin Specification

## Purpose
TBD - created by archiving change implement-packer-plugin-builder. Update Purpose after archive.
## Requirements
### Requirement: Plugin Binary Input
The module SHALL accept a built plugin binary (from `build_binary` output) as input for artifact creation.

#### Scenario: Binary from build-binary
- **WHEN** artifact creation receives a container with built binary at `/work/packer-plugin-{name}`
- **THEN** the module proceeds with creating the complete plugin package

#### Scenario: Binary file directly provided
- **WHEN** caller provides a Dagger File containing the plugin binary
- **THEN** the module uses that file for artifact creation

### Requirement: Git Source for Installation
The module SHALL use the normalized lowercase git_source parameter to register the plugin with Packer. When called via the `build_and_install` workflow, the git_source MAY be auto-detected from go.mod if not explicitly provided.

#### Scenario: Plugin registration with uppercase input
- **WHEN** git_source is `github.com/SolomonHD/packer-plugin-Docker`
- **AND** binary `packer-plugin-docker` is available
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/solomonhd/packer-plugin-docker`

#### Scenario: Plugin registration with auto-detected git_source
- **WHEN** git_source was auto-detected from go.mod in the build_and_install workflow
- **AND** the detected value was `github.com/user/packer-plugin-example`
- **THEN** the install phase uses the auto-detected (and normalized) value for registration
- **AND** the informational message about auto-detection appears in build phase output

#### Scenario: Direct install_plugin call requires git_source
- **WHEN** `install_plugin` function is called directly (not via build_and_install)
- **THEN** the `git_source` parameter remains required
- **AND** cannot be auto-detected since source directory is not available

### Requirement: Packer Container
The module SHALL execute plugin installation inside the official HashiCorp Packer container.

#### Scenario: Default Packer version
- **WHEN** packer_version parameter is not provided
- **THEN** the module uses `hashicorp/packer:latest` image

#### Scenario: Specific Packer version
- **WHEN** packer_version parameter is `1.10.0`
- **THEN** the module uses `hashicorp/packer:1.10.0` image

### Requirement: Installation Artifact Collection
The module SHALL collect all files from the Packer plugin installation directory using the transformed git_source path, including files named with the target OS and architecture.

#### Scenario: Successful installation
- **WHEN** `packer plugins install` completes successfully
- **AND** git_source was `github.com/user/packer-plugin-example`
- **THEN** the module copies all files from `~/.packer.d/plugins/github.com/user/example/`

#### Scenario: Installation output structure with target platform
- **WHEN** plugin is installed for git_source `github.com/user/packer-plugin-example` version `1.0.0`
- **AND** built with `target_os=linux` and `target_arch=amd64`
- **THEN** output directory contains:
  - `packer-plugin-example_v1.0.0_x5.0_linux_amd64` (binary)
  - `packer-plugin-example_v1.0.0_x5.0_linux_amd64_SHA256SUM` (checksum)

#### Scenario: Installation output structure for macOS ARM64
- **WHEN** plugin is installed for git_source `github.com/user/packer-plugin-example` version `1.0.0`
- **AND** built with `target_os=darwin` and `target_arch=arm64`
- **THEN** output directory contains:
  - `packer-plugin-example_v1.0.0_x5.0_darwin_arm64` (binary)
  - `packer-plugin-example_v1.0.0_x5.0_darwin_arm64_SHA256SUM` (checksum)

### Requirement: Installation Output
The module SHALL return a Dagger Directory containing the installation artifacts.

#### Scenario: Directory export
- **WHEN** installation completes successfully
- **THEN** the returned Directory can be exported to the caller's filesystem via `.export()`

#### Scenario: Installation failure
- **WHEN** `packer plugins install` fails
- **THEN** the module surfaces the Packer error output

### Requirement: Build and Install Workflow
The module SHALL provide a composite function that combines build and artifact creation phases to produce production-ready plugin packages.

#### Scenario: Single command workflow
- **WHEN** caller invokes `build_artifacts()` with source, git_source, and version
- **THEN** the module builds the plugin, creates installation artifacts, and returns the complete package
- **AND** artifacts include: binary, checksum file, and metadata

#### Scenario: Workflow export
- **WHEN** caller chains `.export(path=".")` to `build_artifacts()` output
- **THEN** installation files are exported to the specified directory
- **AND** files are ready for use with `packer plugins install --path`

#### Scenario: Auto-detected git_source in workflow
- **WHEN** `build_artifacts()` is called without explicit git_source parameter
- **AND** source directory contains a valid go.mod file
- **THEN** git_source is auto-detected from the module directive
- **AND** the detected value is normalized to lowercase
- **AND** both build and artifact creation phases use the auto-detected value

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

### Requirement: Function Purpose Documentation  
The `build_artifacts` function SHALL be documented as the recommended workflow for creating production-ready plugin packages, producing all files needed for plugin distribution or installation.

#### Scenario: Usage guidance in docstring
- **WHEN** user invokes `dagger functions` or reads function help
- **THEN** the `build-artifacts` docstring clearly indicates it creates complete plugin artifacts
- **AND** specifies the output includes binary, checksum, and metadata files
- **AND** indicates this is the preferred workflow for most use cases

#### Scenario: Primary documentation examples
- **WHEN** user reads the README
- **THEN** `build-artifacts` is featured prominently in the main usage examples
- **AND** examples show typical workflows (basic build, VERSION file usage, cross-compilation)
- **AND** context explains the artifacts are ready for distribution or local installation

### Requirement: Artifact Package Completeness
The `build_artifacts` function SHALL ensure all output files follow Packer plugin distribution conventions and are immediately usable with `packer plugins install --path`.

#### Scenario: Complete artifact package structure
- **WHEN** `build-artifacts` completes successfully
- **THEN** the output directory contains all required files:
  - Plugin binary: `packer-plugin-{name}_v{version}_x5.0_{os}_{arch}[.exe]`
  - Checksum file: `packer-plugin-{name}_v{version}_x5.0_{os}_{arch}_SHA256SUM`
- **AND** file naming follows Packer plugin conventions exactly
- **AND** files are immediately usable without additional processing

#### Scenario: Cross-platform artifact creation
- **WHEN** `build-artifacts` is invoked with `--target-os` and `--target-arch` parameters
- **THEN** artifact filenames reflect the target platform
- **AND** Windows builds include `.exe` extension in binary filename
- **AND** all artifacts are compatible with the target platform's Packer installation

