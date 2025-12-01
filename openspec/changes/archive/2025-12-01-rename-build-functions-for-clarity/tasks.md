# Implementation Tasks

## 1. Rename Python Methods
- [x] 1.1 Rename `build_plugin()` method to `build_binary()` in `main.py`
- [x] 1.2 Rename `build_and_install()` method to `build_artifacts()` in `main.py`
- [x] 1.3 Verify all internal calls to `_build_plugin_internal()` still work correctly
- [x] 1.4 Ensure `@function` decorators remain unchanged

## 2. Update Docstrings
- [x] 2.1 Update docstring for `build_binary()` to emphasize it builds a raw Go binary (intermediate/dev use)
- [x] 2.2 Update docstring for `build_artifacts()` to emphasize it creates production-ready artifacts (binary + checksums)
- [x] 2.3 Review parameter descriptions for accuracy with new context

## 3. Update README.md
- [x] 3.1 Update table of contents to use new function names (`build-binary`, `build-artifacts`)
- [x] 3.2 Restructure "Usage" section to feature `build-artifacts` as primary workflow
- [x] 3.3 Update "Basic Build and Create Artifacts" examples (line 27-44) to use `build-artifacts`
- [x] 3.4 Update "Using VERSION File" examples (line 46-56) to use `build-artifacts`
- [x] 3.5 Rename "Build Plugin Only" section to "Build Binary Only" and update examples (line 78-95)
- [x] 3.6 Update "Update VERSION File Before Build" examples (line 98-108) to use `build-artifacts`
- [x] 3.7 Update "Git Source Auto-Detection" examples (line 132-144) to use `build-artifacts`
- [x] 3.8 Update "Go Version Auto-Detection" examples (line 152-166) to use `build-artifacts`
- [x] 3.9 Update "Custom Go/Packer Versions" examples (line 174-184) to use `build-artifacts`
- [x] 3.10 Update "Cross-Compilation" examples (line 189-216) to use `build-artifacts`
- [x] 3.11 Update "Private Git Server" examples (line 224-234) to use `build-artifacts`
- [x] 3.12 Update parameter table header (line 238): `build-and-install / build-plugin` → `build-artifacts / build-binary`
- [x] 3.13 Update "Output Structure" section header (line 310): reference to `build-and-install` → `build-artifacts`
- [x] 3.14 Update "Development" section examples (line 323-342) to use new names
- [x] 3.15 Search for any remaining references to old names in prose/comments

## 4. Validation
- [x] 4.1 Run `openspec validate rename-build-functions-for-clarity --strict` (validated successfully)
- [x] 4.2 Fix any validation errors (no errors found)
- [x] 4.3 Verify `dagger functions` output shows `build-binary` and `build-artifacts` (confirmed)
- [x] 4.4 Test that all examples in README work with new function names (syntax validated via dagger functions)