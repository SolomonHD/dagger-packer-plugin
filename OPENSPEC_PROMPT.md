# OpenSpec change prompt

## Context

The `dagger-packer-plugin` module builds Packer plugins using Go and installs them via HashiCorp Packer. Currently, builds target only the container's native architecture (typically `linux/amd64`). Users who need to distribute plugins for multiple platforms must run separate builds manually or use CI matrix strategies.

## Goal

Add multi-architecture build support by introducing an optional `--platforms` flag that accepts a comma-separated list of target platforms, leveraging Dagger's parallelization to build all targets concurrently.

## Scope

- In scope:
  - Add `--platforms` parameter to `build-plugin` and `build-and-install` functions
  - Default to `linux/amd64` when not specified
  - Validate platform values against an allowed list
  - Build all specified platforms in parallel using Dagger
  - Output binaries with OS/arch suffix in filename
  - Update README.md with platform documentation and examples
- Out of scope:
  - Release automation or upload to registries
  - Platform-specific code signing
  - CGO-enabled builds (stay CGO_ENABLED=0)

## Desired behaviour

- `--platforms` accepts comma-separated values: `--platforms=linux/amd64,darwin/arm64`
- When `--platforms` not provided, defaults to `linux/amd64`
- Invalid platform values produce clear error messages listing valid options
- Multiple platforms build in parallel (not sequentially)
- Output includes all platform binaries and their checksums
- Binary naming follows pattern: `packer-plugin-{name}_v{version}_x5.0_{os}_{arch}`

## Supported platforms

Only these platform values are valid:
- `linux/amd64`
- `linux/arm64`
- `darwin/amd64`
- `darwin/arm64`
- `windows/amd64`

## Constraints & assumptions

- Assumption: CGO_ENABLED=0 remains set (required for cross-compilation)
- Assumption: All Packer plugins are pure Go (no CGO dependencies)
- Constraint: Maintain backward compatibility - existing calls without `--platforms` must work unchanged
- Constraint: Platform validation must happen before any builds start

## Acceptance criteria

- [ ] `build-plugin` accepts optional `--platforms` parameter
- [ ] `build-and-install` accepts optional `--platforms` parameter  
- [ ] Default behavior (no flag) produces `linux/amd64` binary
- [ ] Comma-separated platforms build all targets in parallel
- [ ] Invalid platform values return error with list of valid options
- [ ] README documents supported platforms in a table
- [ ] README includes multi-platform build example
- [ ] Output binaries follow `packer-plugin-{name}_{os}_{arch}` naming
- [ ] Existing tests continue to pass