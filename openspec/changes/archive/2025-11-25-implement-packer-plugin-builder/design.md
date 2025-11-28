# Design: Packer Plugin Builder Module

## Context

### Background
Packer plugins are Go binaries that follow HashiCorp's plugin architecture. Building these plugins requires:
1. Clearing the `VersionPrerelease` variable via Go ldflags to avoid `-dev` suffixes
2. Installing via Packer's CLI to generate checksum files and proper directory structure

Without automation, developers must remember exact build flags and installation commands, leading to inconsistent builds and broken plugin discovery.

### Constraints
- Must work with any Git hosting provider (GitHub, GitLab, self-hosted)
- Binary naming must follow `packer-plugin-{name}` convention exactly
- No `-dev` suffix in version or binary name (breaks Packer plugin system)
- All operations must be containerized for reproducibility

### Stakeholders
- Plugin developers who want reproducible builds
- CI/CD pipelines that build and publish plugins
- Teams using private Packer plugins from internal git servers

## Goals / Non-Goals

### Goals
- Automate the complete Packer plugin build process
- Provide smart defaults while allowing customization
- Support the full workflow from source to installed plugin
- Make `.gitignore` management automatic

### Non-Goals
- Publishing plugins to registries (out of scope for v1)
- Multi-architecture builds (single architecture per invocation)
- Plugin versioning management beyond what's provided in parameters

## Decisions

### Decision 1: Required `source` Parameter
**Choice**: Make `source` directory parameter required, not optional.

**Rationale**: Avoids context confusion per Dagger module guidelines. When called externally, an optional source with `current_module().source()` fallback would read the module's own files instead of the caller's project.

**Usage Pattern**:
```bash
dagger call -m dagger-packer-plugin build-plugin --source=./packer-plugin-docker ...
```

### Decision 2: Version Detection Strategy
**Choice**: Analyze source code to detect version management pattern before build.

**Detection Algorithm**:
1. Check for `version/VERSION` or `VERSION` file
2. Scan `version/version.go` for `//go:embed VERSION` pattern
3. Scan for hardcoded `var Version = "..."` pattern
4. Report version source type: `file`, `hardcoded`, or `ldflags`

**Rationale**: Different plugins use different version patterns. Detecting the pattern allows:
- Using VERSION file directly when `use_version_file=true`
- Properly constructing ldflags to override any pattern
- Warning about potential version mismatches

### Decision 3: Plugin Name Auto-Detection
**Choice**: Auto-detect plugin name from directory, allow override.

**Algorithm**:
1. Extract directory basename from source path
2. If matches `packer-plugin-{name}`, extract `{name}`
3. Otherwise, use full basename
4. Allow explicit `plugin_name` parameter to override

**Example**:
- `./packer-plugin-docker/` → `docker`
- `./my-custom-plugin/` → `my-custom-plugin`
- `--plugin_name=custom` → `custom` (explicit override)

### Decision 4: Container Image Choices
**Choice**: Use official images for reproducibility.

| Operation | Image | Version |
|-----------|-------|---------|
| Go Build | `golang` | `1.21` (or configurable) |
| Packer Install | `hashicorp/packer` | `latest` (or configurable) |

**Rationale**: Official images are well-maintained and widely cached.

### Decision 5: Function Composition Pattern
**Choice**: Provide both granular functions and composite workflow.

**Granular Functions**:
- `build_plugin()` → Returns container with binary
- `install_plugin()` → Returns container with installed files
- `prep_gitignore()` → Returns updated gitignore file

**Composite Function**:
- `build_and_install()` → Chains build and install, exports artifacts

**Rationale**: Allows users to customize workflow or use single command for common case.

### Decision 6: Version Parameter Strategy
**Choice**: Make `version` optional when `use_version_file=true`.

**Parameter Behavior**:
| `use_version_file` | `version` provided | Behavior |
|--------------------|-------------------|----------|
| `false` (default)  | No | Error: version required |
| `false`            | Yes | Use provided version |
| `true`             | No | Read from VERSION file |
| `true`             | Yes | Use provided version (overrides file) |

**Rationale**: Supports CI/CD workflows where version comes from git tags, and developer workflows where VERSION file is authoritative.

### Decision 7: Output Strategy
**Choice**: Functions return Dagger containers/files, user chains `.export()`.

**Rationale**: 
- Follows Dagger's fluent API pattern
- Allows chaining operations before export
- User controls export destination

**Example**:
```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=. --git-source=github.com/user/plugin --version=1.0.0 \
  export --path=.
```

## Risks / Trade-offs

### Risk: Go Version Compatibility
**Risk**: Plugin may require specific Go version not available in container.
**Mitigation**: Add optional `go_version` parameter defaulting to stable version.

### Risk: Packer Version Compatibility  
**Risk**: Plugin may need specific Packer version for installation.
**Mitigation**: Add optional `packer_version` parameter defaulting to latest.

### Trade-off: Simplicity vs Flexibility
**Choice**: Start simple with smart defaults, add parameters as needed.
**Trade-off**: May need additional releases to support edge cases, but keeps initial API clean.

## Migration Plan
Not applicable - new module implementation.

## Open Questions

1. **Multi-architecture builds**: Should we support building for multiple OS/arch combinations in a single call, or leave that to CI matrix strategies?
   - **Current stance**: Single architecture per call; multi-arch handled by caller.

2. **Plugin verification**: Should we verify the built plugin loads correctly before declaring success?
   - **Current stance**: Out of scope for v1; `packer plugins install` provides basic validation.

## Appendix: Packer Plugin Build Reference

### Standard Build Command
```bash
go build -ldflags="-X github.com/hashicorp/packer-plugin-docker/version.VersionPrerelease=" \
  -o packer-plugin-docker .
```

### Standard Install Command
```bash
packer plugins install --path packer-plugin-docker github.com/hashicorp/packer-plugin-docker
```

### Result Directory Structure
```
~/.packer.d/plugins/
├── github.com/
│   └── hashicorp/
│       └── packer-plugin-docker/
│           ├── packer-plugin-docker_v1.0.0_x5.0_linux_amd64
│           └── packer-plugin-docker_v1.0.0_x5.0_linux_amd64_SHA256SUM