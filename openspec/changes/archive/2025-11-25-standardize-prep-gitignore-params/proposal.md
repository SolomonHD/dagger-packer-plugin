# Change: Standardize prep-gitignore Parameters

## Why

The `prep-gitignore` function has inconsistent parameter naming and behavior compared to other module functions. Other functions (`build-plugin`, `build-and-install`, `detect-version`) use `--source` for directory input and auto-detect plugin name, while `prep-gitignore` requires `--target` and mandatory `--plugin-name`. This creates a confusing user experience.

## What Changes

- **BREAKING**: Rename `--target` parameter to `--source` for consistency
- Make `--plugin-name` parameter optional with auto-detection from source directory name
- Reuse existing `_extract_plugin_name` pattern: strip `packer-plugin-` prefix from directory name
- Update README documentation with new parameter names and examples

## Impact

- Affected specs: `gitignore-prep`
- Affected code: `.dagger/src/dagger_packer_plugin/main.py` (prep_gitignore function)
- Affected docs: `README.md` (prep-gitignore section)
- Breaking change for existing users calling `--target` (must update to `--source`)