# Change: Rename Build Functions for Clarity

## Why

The current function names cause confusion:
- `build-plugin` only compiles a Go binary (not a complete plugin package)
- `build-and-install` creates plugin artifacts but doesn't actually install to Packer's plugin directory

This naming mismatch between function names and their actual behavior creates user confusion and doesn't align with Packer ecosystem terminology.

## What Changes

**BREAKING**: Rename public functions to match their actual behavior:
- `build_plugin()` → `build_binary()` (Python method, CLI: `build-binary`)
- `build_and_install()` → `build_artifacts()` (Python method, CLI: `build-artifacts`)

Documentation updates:
- Feature `build-artifacts` as the primary workflow (most users need complete artifacts)
- Move `build-binary` examples to "Advanced" or "Build Binary Only" sections
- Update all parameter tables and cross-references
- Update all docstrings to reflect new names

## Impact

- **Affected specs**: `build-plugin` (renamed), `install-plugin` (references updated)
- **Affected code**: 
  - `openspec/specs/build-plugin/spec.md` (capability name stays for now, function renamed)
  - `openspec/specs/install-plugin/spec.md` (update references to build function)
  - `.dagger/src/dagger_packer_plugin/main.py` (Python methods)
  - `README.md` (all examples, parameter tables, cross-references)
- **Breaking change**: Pre-v1.0 API, acceptable per module conventions
- **Migration**: Users update CLI calls from `build-plugin` to `build-binary` and `build-and-install` to `build-artifacts`