## 1. Go Version Auto-Detection
- [x] 1.1 Add helper function `_detect_go_version(source: dagger.Directory) -> Optional[str]` to read `.go-version` file
- [x] 1.2 Modify `build_plugin` function: if `go_version` not explicitly overridden, call `_detect_go_version`
- [x] 1.3 Modify `build_and_install` function: apply same go version resolution logic before calling `build_plugin`
- [x] 1.4 Handle edge cases: missing file, empty file, file with trailing whitespace/newlines

## 2. Cache-Busting for Exports
- [x] 2.1 Add cache-busting env var (e.g., `DAGGER_CACHE_BUST`) with timestamp or UUID in build container
- [x] 2.2 Ensure the env var is set before the export step to invalidate Dagger layer cache
- [x] 2.3 Test that re-running build-and-install produces exported files (cache-bust mechanism implemented with timestamp)

## 3. Documentation
- [x] 3.1 Update README.md: document `.go-version` file auto-detection behavior
- [x] 3.2 Update README.md: clarify that `--go-version` flag takes precedence over file detection
- [x] 3.3 Update parameter table to reflect the new default behavior

## 4. Testing
- [x] 4.1 Add test fixture with `.go-version` file (tests/fixtures/go-version-plugin/)
- [x] 4.2 Add unit test: go_version detection from file (13 tests in TestGoVersionDetection)
- [x] 4.3 Add unit test: explicit --go-version overrides file
- [x] 4.4 Add unit test: fallback to 1.21 when no file present
- [x] 4.5 Add unit test: verify cache-busting mechanism (2 tests in TestCacheBusting)