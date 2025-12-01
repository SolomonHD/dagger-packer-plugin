## MODIFIED Requirements

### Requirement: Build and Install Workflow
The module SHALL provide a composite function that combines build and install phases, with support for cross-compilation target parameters.

#### Scenario: Single command workflow
- **WHEN** caller invokes `build_and_install()` with source, git_source, and version
- **THEN** the module builds the plugin, installs it, and returns installation artifacts

#### Scenario: Single command workflow with cross-compilation
- **WHEN** caller invokes `build_and_install()` with source, git_source, version, `target_os=darwin`, and `target_arch=arm64`
- **THEN** the module passes `target_os` and `target_arch` to the build phase
- **AND** the built binary is compiled for darwin/arm64
- **AND** installation artifacts reflect the target platform

#### Scenario: Single command workflow with default targets
- **WHEN** caller invokes `build_and_install()` without `target_os` or `target_arch` parameters
- **THEN** the module uses default `target_os=linux` and `target_arch=amd64`
- **AND** the built binary is compiled for linux/amd64

#### Scenario: Workflow export
- **WHEN** caller chains `.export(path=".")` to `build_and_install()` output
- **THEN** installation files are exported to the specified directory

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