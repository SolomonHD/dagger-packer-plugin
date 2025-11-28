# gitignore-prep Specification

## Purpose
TBD - created by archiving change implement-packer-plugin-builder. Update Purpose after archive.
## Requirements
### Requirement: Plugin Name Input
The module SHALL accept an optional plugin name parameter to override auto-detection. When not provided, the plugin name SHALL be auto-detected from the source directory name.

#### Scenario: Plugin name provided as override
- **WHEN** plugin_name is explicitly provided as `docker`
- **THEN** the module uses `docker` as the plugin name regardless of directory name

#### Scenario: Plugin name auto-detected from directory
- **WHEN** plugin_name is not provided
- **AND** source directory name is `packer-plugin-docker`
- **THEN** the module auto-detects plugin name as `docker`

#### Scenario: Plugin name auto-detected without prefix
- **WHEN** plugin_name is not provided
- **AND** source directory name is `my-custom-plugin`
- **THEN** the module uses `my-custom-plugin` as the plugin name

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

### Requirement: Preserve Existing Content
The module SHALL preserve all existing gitignore entries when adding new ones.

#### Scenario: Existing entries preserved
- **WHEN** gitignore contains entries for `*.log` and `node_modules/`
- **AND** module adds `packer-plugin-docker`
- **THEN** the output gitignore contains all three entries

#### Scenario: Trailing newline
- **WHEN** gitignore is updated
- **THEN** the file ends with a single trailing newline

### Requirement: Gitignore Output
The module SHALL return a Dagger File containing the updated gitignore content.

#### Scenario: File export
- **WHEN** prep_gitignore completes
- **THEN** the returned File can be exported via `.export(path=".gitignore")`

#### Scenario: Multiple plugins
- **WHEN** caller needs to ignore multiple plugin binaries
- **THEN** caller invokes prep_gitignore multiple times or provides a list of names

### Requirement: Plugin Name Lowercase Normalization for Gitignore
The module SHALL normalize the `plugin_name` parameter (auto-detected from go.mod or provided) to lowercase before adding binary entry to gitignore.

#### Scenario: Uppercase plugin name from go.mod normalized
- **WHEN** go.mod contains `module github.com/SolomonHD/packer-plugin-Docker`
- **AND** plugin_name is not provided
- **THEN** the module extracts and normalizes to `docker`
- **AND** outputs warning: `⚠ Warning: plugin-name normalized to lowercase: docker`
- **AND** gitignore entry is `packer-plugin-docker`

#### Scenario: Uppercase explicit plugin name normalized
- **WHEN** plugin_name is `Docker`
- **THEN** the module normalizes to `docker`
- **AND** outputs warning: `⚠ Warning: plugin-name normalized to lowercase: docker`
- **AND** gitignore entry is `packer-plugin-docker`

#### Scenario: Lowercase plugin name unchanged
- **WHEN** plugin_name is `docker` (from go.mod or explicit)
- **THEN** the module uses the name without modification
- **AND** no warning is output
- **AND** gitignore entry is `packer-plugin-docker`

### Requirement: Source Directory Input
The module SHALL accept a source directory parameter where the gitignore file exists or should be created.

#### Scenario: Directory with existing gitignore
- **WHEN** source directory contains a `.gitignore` file
- **THEN** the module reads the existing file before modification

#### Scenario: Directory without gitignore
- **WHEN** source directory does not contain a `.gitignore` file
- **THEN** the module creates a new gitignore file

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

