## 1. Implementation

- [x] 1.1 Update `prep_gitignore` function signature in `.dagger/src/dagger_packer_plugin/main.py`
  - Renamed `target` parameter to `source`
  - Made `plugin_name` parameter optional (default: None)
  - Updated docstring and `Doc()` annotations

- [x] 1.2 Add plugin name auto-detection logic to `prep_gitignore`
  - When `plugin_name` is None, detects from go.mod module path
  - Extracts last segment and applies `_extract_plugin_name` to strip `packer-plugin-` prefix

- [x] 1.3 Update README.md documentation
  - Updated prep-gitignore section with new parameter names
  - Updated example to use `--source=.` instead of `--target=.`
  - Added example with optional `--plugin-name` override
  - Updated parameters table with Default column

## 2. Validation

- [x] 2.1 Test function with only `--source=.` (auto-detection) - verified plugin name detected as "test" from go.mod
- [x] 2.2 Test function with `--source=. --plugin-name=custom` (override) - verified override produces "packer-plugin-mycustom"
- [x] 2.3 Verify existing gitignore content is preserved - verified all original content preserved with new entry appended
- [x] 2.4 Verify idempotent behavior still works - verified diff shows files identical on second run