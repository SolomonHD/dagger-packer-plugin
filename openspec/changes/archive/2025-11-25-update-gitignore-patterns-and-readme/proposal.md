# Change: Improve gitignore patterns and fix README documentation

## Why
1. The current `prep-gitignore` function only adds the base binary name pattern (`packer-plugin-{name}`), which misses the versioned build artifacts that follow Packer's naming convention (`packer-plugin-{name}_v{version}_x5.0_{os}_{arch}`) and their associated checksum files (`*_SHA256SUM`).

2. The README documentation for `build-plugin` is missing `export --path=.` which is required to extract the built artifacts from the container.

## What Changes
- **gitignore patterns**: Modify `prep-gitignore` to generate glob patterns that catch versioned binaries and SHA256SUM files
  - Add pattern: `packer-plugin-{name}_v*` for versioned binaries (covers all versions, API levels, OS, and arch combinations)
  - Add pattern: `*_SHA256SUM` for checksum files
  - Keep existing base binary pattern for compatibility
- **README update**: Add `export --path=.` to the `build-plugin` example to match the pattern used by `build-and-install`

## Impact
- Affected specs: `gitignore-prep`
- Affected code: `main.py` (`prep_gitignore` function), `README.md`
- Non-breaking: Existing gitignore entries are preserved; new patterns are additive