# build-plugin Specification Deltas

## RENAMED Requirements

### Function Name Change
- **FROM**: `build_plugin` (Python method), `build-plugin` (CLI)
- **TO**: `build_binary` (Python method), `build-binary` (CLI)
- **REASON**: Clarify that this function only compiles the Go binary, not a complete plugin package

## MODIFIED Requirements

### Requirement: Build Output
The module SHALL return a Dagger Container containing the built plugin binary. This function is intended for intermediate/development use when only the compiled binary is needed.

#### Scenario: Successful build
- **WHEN** Go build completes successfully via `build-binary` function
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions

#### Scenario: Build failure
- **WHEN** Go build fails (compilation errors) during `build-binary` execution
- **THEN** the module surfaces the build error with Go compiler output

#### Scenario: Intermediate development workflow
- **WHEN** developer needs to test binary compilation without creating complete artifacts
- **THEN** `build-binary` provides the compiled binary in a container for inspection or testing

## ADDED Requirements

### Requirement: Function Purpose Documentation
The `build_binary` function SHALL be documented as an intermediate/development tool for compiling the raw Go binary, while `build_artifacts` (in install-plugin spec) is the recommended workflow for production use.

#### Scenario: Usage guidance in docstring
- **WHEN** user invokes `dagger functions` or reads function help
- **THEN** the `build-binary` docstring clearly indicates it builds only the binary
- **AND** recommends using `build-artifacts` for production-ready plugin packages

#### Scenario: README documentation structure
- **WHEN** user reads the README
- **THEN** primary examples feature `build-artifacts` workflow
- **AND** `build-binary` examples appear in "Advanced" or "Build Binary Only" section
- **AND** context explains when to use each function