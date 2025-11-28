## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Plugin Name Input
The module SHALL accept a plugin name parameter to determine which binary pattern to add to gitignore, normalizing uppercase characters to lowercase.

#### Scenario: Plugin name provided with uppercase
- **WHEN** plugin_name is `Docker`
- **THEN** the module prepares to add `packer-plugin-docker` to gitignore
- **AND** outputs warning about normalization

### Requirement: Gitignore Entry Format
The module SHALL add the plugin binary name (always lowercase) following standard gitignore patterns.

#### Scenario: Binary entry added with normalized name
- **WHEN** plugin_name is `Docker` (uppercase)
- **THEN** the gitignore contains entry `packer-plugin-docker` (lowercase)