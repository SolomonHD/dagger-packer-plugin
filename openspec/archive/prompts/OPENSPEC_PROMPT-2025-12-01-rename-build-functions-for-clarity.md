# OpenSpec change prompt

## Context

The dagger-packer-plugin module currently has confusing function names:
- `build-plugin` - Just compiles the Go binary (no plugin packaging)
- `build-and-install` - Creates complete plugin package with binary + checksums (doesn't actually install to Packer)

This naming causes confusion because:
- "plugin" suggests a complete package, but `build-plugin` only builds a binary
- "install" suggests deploying to Packer's plugin directory, but `build-and-install` just prepares files

## Goal

Rename functions to match Packer ecosystem terminology and clarify their distinct purposes:
- `build-plugin` → `build-binary` (compiles raw Go binary)
- `build-and-install` → `build-artifacts` (creates complete plugin package: binary + metadata + checksums)

Update all documentation to feature `build-artifacts` as the primary function since most users need the complete artifacts, not just the binary.

## Scope

- In scope:
  - Rename `build_plugin` method to `build_binary` in [`main.py`](dagger/modules/dagger-packer-plugin/.dagger/src/dagger_packer_plugin/main.py)
  - Rename `build_and_install` method to `build_artifacts` in [`main.py`](dagger/modules/dagger-packer-plugin/.dagger/src/dagger_packer_plugin/main.py)
  - Update all function calls to internal methods (`_build_plugin_internal`)
  - Update [`README.md`](dagger/modules/dagger-packer-plugin/README.md):
    - Examples and usage sections
    - Parameter tables
    - Cross-references
    - Feature `build-artifacts` prominently as the recommended workflow
  - Update docstrings for renamed functions

- Out of scope:
  - Changes to function behavior or parameters
  - Changes to `detect_version` or `prep_gitignore` functions
  - Changes to cross-compilation logic
  - Changes to internal helper methods

## Desired behavior

After the change:

1. **Function names**:
   - `build-binary` - Compiles the Go plugin binary (intermediate/dev use)
   - `build-artifacts` - Creates production-ready artifacts (binary + checksums)
   - Both functions preserve all existing parameters and behavior

2. **Documentation structure**:
   - Primary examples use `build-artifacts` (most common workflow)
   - `build-binary` examples shown in "Advanced" or "Build Binary Only" section
   - Parameter tables updated with new function names
   - All cross-references use new names

3. **Backward compatibility note**:
   - No backward compatibility needed (pre-v1.0 API can break)
   - Clear migration path in commit message

## Constraints & assumptions

- Assumption: This is a breaking change acceptable for the module (not yet at v1.0 stability)
- Assumption: No external dependencies on the old function names exist
- Constraint: All internal calls to `_build_plugin_internal` must still work
- Constraint: Function decorators (`@function`) remain unchanged
- Constraint: Python method names follow snake_case: `build_binary`, `build_artifacts`

## Acceptance criteria

- [ ] Python method `build_plugin` renamed to `build_binary` in [`main.py`](dagger/modules/dagger-packer-plugin/.dagger/src/dagger_packer_plugin/main.py:482)
- [ ] Python method `build_and_install` renamed to `build_artifacts` in [`main.py`](dagger/modules/dagger-packer-plugin/.dagger/src/dagger_packer_plugin/main.py:825)
- [ ] All docstrings updated for renamed functions
- [ ] [`README.md`](dagger/modules/dagger-packer-plugin/README.md) updated:
  - Table of contents uses new names
  - All usage examples use new names
  - Primary examples feature `build-artifacts` workflow
  - Parameter tables reference correct function names
- [ ] No references to old names remain in documentation
- [ ] Dagger functions list shows `build-binary` and `build-artifacts` when running `dagger functions`