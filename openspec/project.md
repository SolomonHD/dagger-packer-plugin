# Project Context

## Purpose
Dagger module (Python SDK) that automates building and installing HashiCorp Packer plugins following the official build process. Ensures reproducible plugin builds without `-dev` suffixes that would break the Packer plugin system, and handles proper plugin installation.

## Tech Stack
- **Runtime**: Dagger (containerized pipeline)
- **SDK**: Python (dagger-io)
- **Build Target**: Go (Packer plugins are written in Go)
- **Container Images**: Official Go container, HashiCorp Packer container

## Project Conventions

### Code Style
- Follow Dagger Python SDK conventions
- Use `@object_type` and `@function` decorators
- All public functions return `str` for CLI compatibility
- Use `Annotated[type, Doc("description")]` for parameters
- Async functions for Dagger operations
- Emoji indicators for output: `✔` success, `✖` failure

### Architecture Patterns
- Containerized operations for reproducibility
- Smart defaults with auto-detection (e.g., plugin name from directory)
- Required parameters for external module usage (avoid context confusion)
- Chained Dagger operations using fluent API

### Testing Strategy
- Unit tests with pytest (async)
- Integration tests via `dagger call` commands
- Test against multiple Packer plugin structures

### Git Workflow
- Semantic versioning with `v` prefix (e.g., `v1.0.0`)
- Module name in dagger.json may differ from repository name

## Domain Context

### Packer Plugin Build Requirements
- Packer plugins are Go binaries following naming convention: `packer-plugin-{name}`
- Official build uses ldflags to clear `VersionPrerelease` variable (removes `-dev` suffix)
- Command: `go build -ldflags="-X {git-source}/version.VersionPrerelease="`
- The `-dev` suffix in version breaks Packer's plugin discovery

### Packer Plugin Installation
- Packer uses `packer plugins install --path <binary> <git-source>` for local installation
- Installed plugins go to `~/.packer.d/plugins/` directory
- Files include: checksums, binary, and metadata files

### Plugin Name Detection
- Plugin directories follow pattern: `packer-plugin-{name}`
- Name can be auto-detected by stripping `packer-plugin-` prefix from directory name
- Users can manually override with `plugin_name` parameter

## Important Constraints
- **No `-dev` suffix**: Binary name and version must never append `-dev`
- **Git source flexibility**: Must support any git hosting (GitHub, GitLab, private servers)
- **Reproducible builds**: All build operations must run in containers
- **Binary output location**: Must export to invoking repository's working directory

## External Dependencies
- **Go container**: For building plugin binaries
- **HashiCorp Packer container**: For plugin installation
- **Git source path**: User provides git path (e.g., `github.com/hashicorp/docker`)
