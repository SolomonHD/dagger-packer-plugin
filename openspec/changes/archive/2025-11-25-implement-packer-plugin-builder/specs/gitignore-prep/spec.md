# Gitignore Prep Capability

## ADDED Requirements

### Requirement: Plugin Name Input
The module SHALL accept a plugin name parameter to determine which binary pattern to add to gitignore.

#### Scenario: Plugin name provided
- **WHEN** plugin_name is `docker`
- **THEN** the module prepares to add `packer-plugin-docker` to gitignore

### Requirement: Target Directory Input
The module SHALL accept a target directory where the gitignore file exists or should be created.

#### Scenario: Directory with existing gitignore
- **WHEN** target directory contains a `.gitignore` file
- **THEN** the module reads the existing file before modification

#### Scenario: Directory without gitignore
- **WHEN** target directory does not contain a `.gitignore` file
- **THEN** the module creates a new gitignore file

### Requirement: Gitignore Entry Format
The module SHALL add the plugin binary name following standard gitignore patterns.

#### Scenario: Binary entry added
- **WHEN** plugin_name is `docker`
- **THEN** the gitignore contains entry `packer-plugin-docker`

#### Scenario: Entry with comment
- **WHEN** adding a new plugin binary entry
- **THEN** the entry MAY be preceded by a comment `# Packer plugin binary`

### Requirement: Idempotent Updates
The module SHALL not duplicate entries if the plugin binary is already in gitignore.

#### Scenario: Entry already exists
- **WHEN** gitignore already contains `packer-plugin-docker`
- **AND** plugin_name is `docker`
- **THEN** the gitignore content remains unchanged

#### Scenario: Entry does not exist
- **WHEN** gitignore does not contain `packer-plugin-docker`
- **AND** plugin_name is `docker`
- **THEN** the gitignore is updated with the new entry

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