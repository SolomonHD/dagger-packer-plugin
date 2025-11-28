# OpenSpec change prompt

## Context

The `dagger-packer-plugin` module requires users to manually specify `--git-source` (e.g., `github.com/SolomonHD/packer-plugin-ansible-navigator`) when building Packer plugins. This value is already present in the plugin's `go.mod` file as the module path, creating unnecessary duplication and potential for user error.

## Goal

Auto-detect `--git-source` from the `go.mod` file in the source directory, making the parameter optional when building from a properly structured Go-based Packer plugin.

## Scope

- In scope:
  - Read and parse `go.mod` from the `--source` directory
  - Extract the module path as the default `git-source` value
  - Make `--git-source` optional (auto-detected when not provided)
  - Apply existing lowercase normalization to auto-detected values
  - Display informational message when git-source is auto-detected
  - Fall back to requiring `--git-source` if `go.mod` is missing or unparseable
  - Update README.md with auto-detection documentation
- Out of scope:
  - Parsing other Go project files (go.work, vendor modules)
  - Validating that the module path is a valid git URL
  - Caching go.mod parsing results

## Desired behavior

- When `--git-source` not provided and `go.mod` exists:
  - Parse `module <path>` from first lines of `go.mod`
  - Use extracted path as `git-source`
  - Display: `ℹ Using git-source from go.mod: github.com/user/plugin`
- When `--git-source` explicitly provided:
  - Use provided value (existing behavior unchanged)
- When `--git-source` not provided and `go.mod` missing/invalid:
  - Return clear error: `Error: --git-source required (could not auto-detect from go.mod)`
- Lowercase normalization applies to auto-detected values

## Constraints & assumptions

- Assumption: All Packer plugins have a `go.mod` file with a module declaration
- Assumption: The module path in `go.mod` matches the intended git-source
- Constraint: Maintain backward compatibility - explicit `--git-source` always takes precedence
- Constraint: Only parse the `module` directive, ignore other go.mod content

## Acceptance criteria

- [ ] `build-plugin` auto-detects `git-source` from `go.mod` when not provided
- [ ] `build-and-install` auto-detects `git-source` from `go.mod` when not provided
- [ ] Explicit `--git-source` parameter overrides auto-detection
- [ ] Missing `go.mod` produces clear error requesting `--git-source`
- [ ] Invalid/unparseable `go.mod` produces clear error
- [ ] Auto-detected values are normalized to lowercase
- [ ] Informational message displayed when git-source is auto-detected
- [ ] README documents auto-detection behavior
- [ ] README shows simplified example without `--git-source`
- [ ] Existing tests continue to pass