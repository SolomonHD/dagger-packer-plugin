# Change: Auto-detect git-source from go.mod

## Why

The `dagger-packer-plugin` module requires users to manually specify `--git-source` (e.g., `github.com/SolomonHD/packer-plugin-ansible-navigator`) when building Packer plugins. This value is already present in the plugin's `go.mod` file as the module path, creating unnecessary duplication and potential for user error.

Auto-detecting this value from `go.mod` simplifies the user experience and follows the existing pattern already used for `prep-gitignore` function's plugin name auto-detection.

## What Changes

- **MODIFIED**: `git_source` parameter becomes optional in `build-plugin` and `build-and-install` functions
- **ADDED**: Auto-detection of `git_source` from `go.mod` module path when not provided
- **ADDED**: Informational message when git-source is auto-detected
- **ADDED**: Clear error message when git-source cannot be determined (missing go.mod AND no explicit parameter)
- **MODIFIED**: `install-plugin` benefits from upstream auto-detection through `build-and-install` workflow
- Lowercase normalization continues to apply to auto-detected values

## Impact

- Affected specs: `build-plugin`, `install-plugin`
- Affected code: `main.py` - parameter handling for `build_plugin` and `build_and_install` functions
- Backward compatible: explicit `--git-source` continues to work and takes precedence
- No breaking changes: functions that previously required explicit git-source still accept it