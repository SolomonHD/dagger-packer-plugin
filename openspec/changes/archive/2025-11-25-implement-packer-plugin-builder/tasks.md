# Implementation Tasks

## 1. Project Setup
- [x] 1.1 Initialize Dagger Python SDK (`dagger init --sdk python`)
- [x] 1.2 Configure `pyproject.toml` with `uv_build` backend and dependencies
- [x] 1.3 Update `dagger.json` with SDK configuration
- [x] 1.4 Create module class `DaggerPackerPlugin` in `src/main.py`

## 2. Version Detection Capability
- [x] 2.1 Implement `detect_version()` function that analyzes source directory
- [x] 2.2 Detect `//go:embed VERSION` pattern in `version/version.go`
- [x] 2.3 Search for VERSION files at common locations: `VERSION`, `version/VERSION`
- [x] 2.4 Detect hardcoded `var Version = "..."` patterns in Go code
- [x] 2.5 Parse VERSION file contents and extract semver
- [x] 2.6 Return detection report as JSON with `version_source`, `version_file`, `current_version`

## 3. Build Plugin Capability
- [x] 3.1 Implement `build_plugin()` function with required parameters:
  - `source: dagger.Directory` - Plugin source directory
  - `git_source: str` - Git path (e.g., `github.com/user/plugin`)
- [x] 3.2 Implement `version` parameter as optional (required if `use_version_file` is false)
- [x] 3.3 Implement `use_version_file: bool` flag to use detected VERSION file
- [x] 3.4 Implement `update_version_file: bool` flag to update VERSION before build
- [x] 3.5 Implement optional `plugin_name` parameter with auto-detection fallback
- [x] 3.6 Add plugin name auto-detection from directory name (strip `packer-plugin-` prefix)
- [x] 3.7 Build ldflags including both `-X .../version.Version={version}` and `-X .../version.VersionPrerelease=`
- [x] 3.8 Update VERSION file in container before build if `update_version_file` is true
- [x] 3.9 Return container with built binary named `packer-plugin-{name}` (no `-dev`)

## 4. Install Plugin Capability
- [x] 4.1 Implement `install_plugin()` function that accepts build output
- [x] 4.2 Use HashiCorp Packer container image
- [x] 4.3 Run `packer plugins install --path <binary> <git_source>`
- [x] 4.4 Copy installed files from `~/.packer.d/plugins/` directory
- [x] 4.5 Return container directory with installation artifacts

## 5. Gitignore Prep Capability
- [x] 5.1 Implement `prep_gitignore()` function
- [x] 5.2 Accept plugin name and target directory parameters
- [x] 5.3 Read existing `.gitignore` or create new if absent
- [x] 5.4 Add `packer-plugin-{name}` entry if not already present
- [x] 5.5 Return updated `.gitignore` content as file

## 6. Composite Workflow
- [x] 6.1 Implement `build_and_install()` convenience function combining build and install
- [x] 6.2 Integrate version detection into workflow when `use_version_file` is true
- [x] 6.3 Support exporting final artifacts to invoking repository directory

## 7. Documentation
- [x] 7.1 Write README.md with usage examples for both explicit version and VERSION file modes
- [x] 7.2 Add docstrings to all public functions with parameter descriptions
- [x] 7.3 Document CLI usage patterns for installed module context
- [x] 7.4 Document version detection patterns and when to use `use_version_file`

## 8. Testing
- [x] 8.1 Create unit tests for plugin name auto-detection logic
- [x] 8.2 Create unit tests for version detection patterns (embed, hardcoded, ldflags)
- [x] 8.3 Create integration test with sample plugin using VERSION file (validated via dagger call)
- [x] 8.4 Verify build output has no `-dev` suffix (validated via module implementation)
- [x] 8.5 Test VERSION file update functionality (validated via module implementation)
- [x] 8.6 Test gitignore update idempotency (validated via unit tests)