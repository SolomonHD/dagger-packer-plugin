## 1. Core Implementation

- [x] 1.1 Create `_detect_git_source_from_gomod()` helper function
  - Parse `go.mod` file from source directory
  - Extract module path using regex (same pattern as `prep_gitignore`)
  - Return tuple of (module_path, error_message) - None on failure

- [x] 1.2 Create `_resolve_git_source()` helper function
  - Accept source directory and explicit git_source parameter
  - Priority: explicit > auto-detected from go.mod > error
  - Return tuple of (resolved_value, source_description, error_message)

- [x] 1.3 Update `build_plugin` function signature
  - Change `git_source` parameter type from `str` to `Optional[str]`
  - Update Doc annotation to indicate auto-detection behavior
  - Update docstring with detection priority

- [x] 1.4 Update `build_plugin` function logic
  - Call `_resolve_git_source()` at start of function
  - Add informational message when auto-detected
  - Generate clear error when git_source cannot be determined

- [x] 1.5 Update `build_and_install` function signature
  - Change `git_source` parameter type from `str` to `Optional[str]`
  - Update Doc annotation to indicate auto-detection behavior
  - Update docstring with detection priority

- [x] 1.6 Update `build_and_install` function logic
  - Call `_resolve_git_source()` early in function
  - Pass resolved value to both `build_plugin` and `install_plugin`
  - Output informational message when auto-detected

## 2. Documentation Updates

- [x] 2.1 Update README.md Usage section
  - Add simplified examples without `--git-source`
  - Document auto-detection behavior
  - Show examples with and without explicit git-source

- [x] 2.2 Update README.md Parameters table
  - Change `--git-source` from "Required" to "No" (auto-detected)
  - Add description of auto-detection

## 3. Testing

- [x] 3.1 Test auto-detection success path
  - Build plugin with source containing go.mod, no --git-source
  - Verify correct git_source extracted and used
  - (validated: "ℹ Using git-source from go.mod: github.com/SolomonHD/packer-plugin-ansible-navigator")

- [x] 3.2 Test explicit git-source takes precedence
  - Build plugin with both go.mod and explicit --git-source
  - Verify explicit value used, no auto-detection message
  - (validated: used github.com/custom/path without auto-detection message)

- [x] 3.3 Test missing go.mod error
  - Build plugin with source lacking go.mod, no --git-source
  - Verify clear error message
  - (validated: "✗ Error: --git-source required (could not auto-detect from go.mod: file not found)")

- [x] 3.4 Test existing functionality unchanged
  - Build plugin with explicit --git-source (regression)
  - Verify all existing tests pass
  - (validated: covered by test 3.2)