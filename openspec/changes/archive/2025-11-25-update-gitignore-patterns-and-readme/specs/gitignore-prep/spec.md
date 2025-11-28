## ADDED Requirements

### Requirement: Versioned Binary Gitignore Patterns
The module SHALL generate gitignore patterns that match versioned build artifacts following Packer's naming convention.

#### Scenario: Versioned binary pattern added
- **WHEN** prep_gitignore generates patterns for plugin_name `docker`
- **THEN** the gitignore contains pattern `packer-plugin-docker_v*` to match versioned binaries

#### Scenario: Pattern matches full versioned binary name
- **WHEN** gitignore contains pattern `packer-plugin-docker_v*`
- **THEN** the pattern matches files like `packer-plugin-docker_v1.0.10_x5.0_linux_amd64`
- **AND** the pattern matches files like `packer-plugin-docker_v2.0.0_x5.0_darwin_arm64`

### Requirement: SHA256SUM File Gitignore Pattern
The module SHALL generate a gitignore pattern that matches SHA256SUM checksum files produced by Packer plugin installation.

#### Scenario: SHA256SUM pattern added
- **WHEN** prep_gitignore generates patterns for any plugin
- **THEN** the gitignore contains pattern `*_SHA256SUM` to match checksum files

#### Scenario: SHA256SUM pattern matches checksum files
- **WHEN** gitignore contains pattern `*_SHA256SUM`
- **THEN** the pattern matches files like `packer-plugin-docker_v1.0.10_x5.0_linux_amd64_SHA256SUM`

## MODIFIED Requirements

### Requirement: Gitignore Entry Format
The module SHALL add gitignore entries (always lowercase) following standard gitignore glob patterns. Entries include the base binary name, versioned binary pattern, and SHA256SUM pattern.

#### Scenario: Binary entry added with normalized name
- **WHEN** plugin_name is `Docker` (uppercase)
- **THEN** the gitignore contains entry `packer-plugin-docker` (base binary, lowercase)
- **AND** the gitignore contains entry `packer-plugin-docker_v*` (versioned pattern)
- **AND** the gitignore contains entry `*_SHA256SUM` (checksum pattern)

### Requirement: Idempotent Updates
The module SHALL not duplicate entries if patterns are already in gitignore. Each pattern is checked independently.

#### Scenario: Entry already exists
- **WHEN** gitignore already contains `packer-plugin-docker` and `packer-plugin-docker_v*` and `*_SHA256SUM`
- **AND** plugin_name is `docker`
- **THEN** the gitignore content remains unchanged

#### Scenario: Partial entries exist
- **WHEN** gitignore already contains `packer-plugin-docker` but not `packer-plugin-docker_v*`
- **AND** plugin_name is `docker`
- **THEN** only the missing patterns are added