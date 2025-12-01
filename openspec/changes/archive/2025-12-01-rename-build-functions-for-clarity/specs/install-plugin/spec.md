# install-plugin Specification Deltas

## RENAMED Requirements

### Function Name Change
- **FROM**: `build_and_install` (Python method), `build-and-install` (CLI)
- **TO**: `build_artifacts` (Python method), `build-artifacts` (CLI)
- **REASON**: Clarify that this function creates production-ready plugin artifacts (binary + checksums + metadata) but doesn't actually install to Packer's plugin directory. The term "install" was misleading.

## MODIFIED Requirements

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

### Requirement: Plugin Binary Input
The module SHALL accept a built plugin binary (from `build_binary` output) as input for artifact creation.

#### Scenario: Binary from build-binary
- **WHEN** artifact creation receives a container with built binary at `/work/packer-plugin-{name}`
- **THEN** the module proceeds with creating the complete plugin package

#### Scenario: Binary file directly provided
- **WHEN** caller provides a Dagger File containing the plugin binary
- **THEN** the module uses that file for artifact creation

## ADDED Requirements

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