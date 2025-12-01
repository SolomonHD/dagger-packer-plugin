# Change: Add Cross-Compilation Support

## Why
The `dagger-packer-plugin` module currently builds Packer plugins for the container's architecture (e.g., `linux/amd64`) rather than allowing users to specify a target platform. This causes "Exec format error" when attempting to run the compiled plugin on a different platform (e.g., building inside a Linux container but running on macOS).

## What Changes
- **ADDED** `target_os` parameter to `build_plugin` function (default: `linux`)
- **ADDED** `target_arch` parameter to `build_plugin` function (default: `amd64`)
- **MODIFIED** Go build process to set `GOOS` and `GOARCH` environment variables
- **MODIFIED** Binary naming to include correct `_{os}_{arch}` suffix in output
- **MODIFIED** `build_and_install` workflow to accept and pass through `target_os` and `target_arch` parameters
- **MODIFIED** README documentation with new parameters and cross-compilation examples

## Out of Scope
- Multi-architecture builds (building for multiple targets in one call)
- Changes to `detect_version`, `prep_gitignore`, or `install_plugin` function signatures

## Impact
- **Affected specs**: `build-plugin`, `install-plugin`
- **Affected code**: `.dagger/src/main/__init__.py` (build functions), `README.md`
- **Breaking changes**: None - new parameters are optional with sensible defaults

## Default Behavior
When `target_os` and `target_arch` are not provided:
- Defaults to `linux` and `amd64` (Packer's most common deployment target)
- Maintains backward compatibility with existing workflows
- Existing calls without these parameters will continue to work identically