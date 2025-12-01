# OpenSpec change prompt

## Context
The `dagger-packer-plugin` module builds Packer plugins but does not set `GOOS`/`GOARCH` during Go compilation. This causes binaries to be compiled for the container's architecture (e.g., `linux/amd64`) rather than the user's host, resulting in "Exec format error" when running the plugin.

## Goal
Add cross-compilation support so users can build Packer plugins for any target OS/architecture, defaulting to the host platform when not specified.

## Scope
- In scope:
  - Add `target_os` and `target_arch` parameters to `build_plugin` and `build_and_install`
  - Set `GOOS` and `GOARCH` environment variables during Go build
  - Update binary naming to include correct `{os}_{arch}` suffix
  - Update README with new parameters and examples
- Out of scope:
  - Multi-architecture builds (building for multiple targets in one call)
  - Changes to `detect_version`, `prep_gitignore`, or `install_plugin` signatures

## Desired behavior
- When `target_os` and `target_arch` are not provided, default to `linux` and `amd64` (Packer's most common deployment target)
- When provided, use the specified values for cross-compilation
- The built binary should be executable on the target platform
- `./binary describe` should output valid JSON with plugin metadata on the target platform

## Constraints & assumptions
- Assume `CGO_ENABLED=0` remains set (pure Go, no C dependencies)
- Assume Packer plugins only need single-target builds (not fat/universal binaries)
- The `packer plugins install` step runs inside the Packer container, so architecture matching there is less critical

## Acceptance criteria
- [ ] `build_plugin` accepts optional `target_os` (default: `linux`) and `target_arch` (default: `amd64`) parameters
- [ ] `build_and_install` accepts the same parameters and passes them to `build_plugin`
- [ ] Go build sets `GOOS` and `GOARCH` environment variables from these parameters
- [ ] Binary name includes correct `_{os}_{arch}` suffix in output
- [ ] README documents new parameters with examples for cross-compilation
- [ ] Existing tests continue to pass (if any)