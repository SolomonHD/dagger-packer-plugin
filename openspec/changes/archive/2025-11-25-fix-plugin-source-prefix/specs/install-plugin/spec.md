## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Git Source for Installation
The module SHALL use the git_source parameter to register the plugin with Packer, after transforming it to remove the `packer-plugin-` prefix from the repository name.

#### Scenario: Plugin registration
- **WHEN** git_source is `github.com/hashicorp/packer-plugin-docker`
- **AND** binary `packer-plugin-docker` is available
- **THEN** the module runs `packer plugins install --path packer-plugin-docker github.com/hashicorp/docker`

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