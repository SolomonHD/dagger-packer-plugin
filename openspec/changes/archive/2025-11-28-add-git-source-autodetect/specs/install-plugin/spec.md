## MODIFIED Requirements

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