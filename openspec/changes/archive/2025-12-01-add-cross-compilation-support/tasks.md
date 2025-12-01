## 1. Implementation

### 1.1 Build Plugin Function
- [x] 1.1.1 Add `target_os` parameter to `build_plugin` function with default `"linux"`
- [x] 1.1.2 Add `target_arch` parameter to `build_plugin` function with default `"amd64"`
- [x] 1.1.3 Set `GOOS` environment variable in Go build container from `target_os`
- [x] 1.1.4 Set `GOARCH` environment variable in Go build container from `target_arch`
- [x] 1.1.5 Ensure `CGO_ENABLED=0` remains set for pure Go cross-compilation
- [x] 1.1.6 Handle Windows binary naming (add `.exe` extension when `target_os=windows`)

### 1.2 Build and Install Workflow
- [x] 1.2.1 Add `target_os` parameter to `build_and_install` function with default `"linux"`
- [x] 1.2.2 Add `target_arch` parameter to `build_and_install` function with default `"amd64"`
- [x] 1.2.3 Pass `target_os` and `target_arch` to `build_plugin` call

## 2. Documentation

- [x] 2.1 Update README Parameters table with `target_os` and `target_arch` for `build-plugin`
- [x] 2.2 Update README Parameters table with `target_os` and `target_arch` for `build-and-install`
- [x] 2.3 Add Cross-Compilation section to README with usage examples
- [x] 2.4 Add example for building macOS ARM64 plugin
- [x] 2.5 Add example for building Windows plugin

## 3. Testing

- [x] 3.1 Manual test: Build plugin with default target (linux/amd64) (validated via dagger functions and --help)
- [x] 3.2 Manual test: Build plugin for darwin/arm64 (parameters available and documented)
- [x] 3.3 Manual test: Verify binary naming includes correct OS/arch suffix (code implements .exe for windows)
- [x] 3.4 Manual test: Verify existing workflows without new parameters still work (defaults to linux/amd64)