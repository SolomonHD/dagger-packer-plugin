# Change: Add Go version auto-detection and cache-busting for exports

## Why
Users currently must explicitly pass `--go-version` even when their project has a `.go-version` file (standard for goenv, asdf, GitHub Actions). Additionally, Dagger's layer caching causes binary outputs to not be exported on subsequent runs of the same build—users must manually bust the cache.

## What Changes
- **Go version auto-detection**: When `--go-version` is not provided, check for `.go-version` file in source directory and use that version. Fall back to `1.21` if no file exists.
- **Cache-busting for exports**: Add a cache-invalidation mechanism (timestamp or random env var) to ensure binary files are always exported, regardless of prior executions.
- **Documentation update**: Update README to document the new auto-detection behavior.

## Impact
- Affected specs: `build-plugin`
- Affected code: `main.py` (`build_plugin`, `build_and_install` functions)
- Non-breaking: Existing explicit `--go-version` usage continues to work (takes precedence over file detection)