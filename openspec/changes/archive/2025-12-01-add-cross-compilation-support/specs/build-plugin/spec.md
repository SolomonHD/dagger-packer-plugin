## ADDED Requirements

### Requirement: Target Operating System
The module SHALL accept an optional `target_os` parameter specifying the target operating system for cross-compilation.

#### Scenario: Default target OS when not provided
- **WHEN** `target_os` parameter is not provided
- **THEN** the module defaults to `linux`
- **AND** the Go build runs with `GOOS=linux` environment variable

#### Scenario: Explicit target OS provided
- **WHEN** `target_os` parameter is `darwin`
- **THEN** the Go build runs with `GOOS=darwin` environment variable

#### Scenario: Windows target OS
- **WHEN** `target_os` parameter is `windows`
- **THEN** the Go build runs with `GOOS=windows` environment variable
- **AND** the output binary has `.exe` extension

### Requirement: Target Architecture
The module SHALL accept an optional `target_arch` parameter specifying the target CPU architecture for cross-compilation.

#### Scenario: Default target architecture when not provided
- **WHEN** `target_arch` parameter is not provided
- **THEN** the module defaults to `amd64`
- **AND** the Go build runs with `GOARCH=amd64` environment variable

#### Scenario: ARM64 target architecture
- **WHEN** `target_arch` parameter is `arm64`
- **THEN** the Go build runs with `GOARCH=arm64` environment variable

#### Scenario: 386 target architecture
- **WHEN** `target_arch` parameter is `386`
- **THEN** the Go build runs with `GOARCH=386` environment variable

### Requirement: Cross-Compilation Environment
The module SHALL set `GOOS`, `GOARCH`, and `CGO_ENABLED=0` environment variables during the Go build process.

#### Scenario: Full cross-compilation environment
- **WHEN** building with `target_os=darwin` and `target_arch=arm64`
- **THEN** the Go build container has environment variables:
  - `GOOS=darwin`
  - `GOARCH=arm64`
  - `CGO_ENABLED=0`

#### Scenario: Default cross-compilation environment
- **WHEN** building without specifying `target_os` or `target_arch`
- **THEN** the Go build container has environment variables:
  - `GOOS=linux`
  - `GOARCH=amd64`
  - `CGO_ENABLED=0`

## MODIFIED Requirements

### Requirement: Build Output
The module SHALL return a Dagger Container containing the built plugin binary with the target OS and architecture reflected in the output filename.

#### Scenario: Successful build with default target
- **WHEN** Go build completes successfully with default `target_os=linux` and `target_arch=amd64`
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions
- **AND** the binary is compiled for linux/amd64 platform

#### Scenario: Successful build for macOS ARM64
- **WHEN** Go build completes successfully with `target_os=darwin` and `target_arch=arm64`
- **THEN** the container contains file `/work/packer-plugin-{name}` with executable permissions
- **AND** the binary is compiled for darwin/arm64 platform

#### Scenario: Successful build for Windows
- **WHEN** Go build completes successfully with `target_os=windows` and `target_arch=amd64`
- **THEN** the container contains file `/work/packer-plugin-{name}.exe` with executable permissions
- **AND** the binary is compiled for windows/amd64 platform

#### Scenario: Build failure
- **WHEN** Go build fails (compilation errors)
- **THEN** the module surfaces the build error with Go compiler output