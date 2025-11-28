# Change: Implement Packer Plugin Builder Dagger Module

## Why
Packer plugin development requires a specific build process that includes clearing the `VersionPrerelease` variable to avoid `-dev` suffixes that break Packer's plugin discovery system. Additionally, installing plugins locally requires running Packer's installation command inside a container for reproducibility. This Dagger module automates both processes, ensuring consistent, reproducible plugin builds and installations across any environment.

Different plugins handle versioning in different ways—some use embedded VERSION files (via `//go:embed`), others hardcode version strings in Go code, and some expect version injection via ldflags. The module must detect these patterns and handle versioning appropriately.

## What Changes

### New Capabilities
- **build-plugin**: Compile Packer plugins using Go with proper ldflags to eliminate `-dev` suffixes
- **install-plugin**: Install built plugins using HashiCorp Packer container and export installation artifacts
- **gitignore-prep**: Manage `.gitignore` entries to prevent committing binary artifacts
- **version-detection**: Analyze plugin source to detect version management patterns and support intelligent version handling

### Key Features
- Auto-detect plugin name from directory structure (`packer-plugin-{name}` pattern)
- **Detect version source**: Identify if plugin uses VERSION file, hardcoded version, or ldflags pattern
- **Use VERSION file**: Option to use existing VERSION file as authoritative version source
- **Override any pattern**: Use ldflags to override version regardless of how plugin manages it
- Support any git hosting service (GitHub, GitLab, private servers)
- Containerized operations for reproducibility
- Single workflow combining build and install phases

## Impact
- **Affected specs**: Initial creation of `build-plugin`, `install-plugin`, `gitignore-prep`, `version-detection` capabilities
- **Affected code**: New Python Dagger module implementation at `src/main.py`
- **Dependencies**: Go container, HashiCorp Packer container

## Breaking Changes
None - this is a new module implementation.

## Success Criteria
1. Module can build any standard Packer plugin without `-dev` suffix
2. Module detects version management pattern (VERSION file, hardcoded, ldflags)
3. Module can use VERSION file contents when `--use-version-file` flag is set
4. Module can override any version pattern with explicit `--version` parameter
5. Built plugins install correctly via `packer plugins install`
6. Installation artifacts export to invoking repository
7. `.gitignore` properly updated to exclude plugin binaries