## MODIFIED Requirements

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

### Requirement: Source Directory Input
The module SHALL accept a source directory parameter where the gitignore file exists or should be created.

#### Scenario: Directory with existing gitignore
- **WHEN** source directory contains a `.gitignore` file
- **THEN** the module reads the existing file before modification

#### Scenario: Directory without gitignore
- **WHEN** source directory does not contain a `.gitignore` file
- **THEN** the module creates a new gitignore file

## RENAMED Requirements

- FROM: `### Requirement: Target Directory Input`
- TO: `### Requirement: Source Directory Input`