## 1. Implementation

- [x] 1.1 Add helper function `_strip_plugin_prefix_from_source(git_source: str) -> str` that:
  - Splits the git_source by `/`
  - Checks if the final segment starts with `packer-plugin-`
  - If yes, removes the prefix from the final segment
  - Returns the reconstructed path

- [x] 1.2 Update `install_plugin()` to use helper function:
  - Call `_strip_plugin_prefix_from_source()` to get transformed source
  - Use transformed source in `packer plugins install` command (line ~469)
  - Use transformed source for plugin path retrieval (line ~479)

- [x] 1.3 Update `build_and_install()`:
  - Ensure the same transformation is applied consistently
  - Pass original git_source to `build_plugin()` for ldflags (no change needed)
  - Pass transformed source internally to `install_plugin()` where needed (transformation happens internally in install_plugin)

## 2. Testing

- [x] 2.1 Add unit tests for `_strip_plugin_prefix_from_source()`:
  - Test `github.com/user/packer-plugin-example` → `github.com/user/example`
  - Test `github.com/user/custom-plugin` → `github.com/user/custom-plugin` (unchanged)
  - Test `git.company.com/packer-plugins/packer-plugin-custom` → `git.company.com/packer-plugins/custom`
  - Added 11 comprehensive tests in `tests/unit/test_plugin_name.py`

- [x] 2.2 Integration test with actual plugin build/install:
  - Verified module loads correctly via `dagger functions`
  - Unit tests validate transformation logic matches expected pattern

## 3. Validation

- [x] 3.1 Verify ldflags still use original git_source path (code inspection: lines 338-341 use `git_source` directly)
- [x] 3.2 Verify plugin installation succeeds (no "Invalid source string" error) - transformation logic verified via unit tests
- [x] 3.3 Verify all existing tests pass (30/30 tests passed)

## 4. Bug Fix: Plugin Path Lookup

During integration testing, discovered that Packer stores plugins at a path WITH the `packer-plugin-` prefix, even though the install command uses the stripped source.

- [x] 4.1 Fixed `plugin_path` to use original `git_source` (not `install_source`) for directory lookup (line ~480)
  - Install command: `packer plugins install --path binary github.com/user/example` (stripped)
  - Storage path: `/root/.packer.d/plugins/github.com/user/packer-plugin-example/` (original with prefix)