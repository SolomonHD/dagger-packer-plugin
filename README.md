# Dagger Packer Plugin Builder

A Dagger module (Python SDK) that automates building and installing Packer plugins following HashiCorp's official build process. Ensures reproducible builds without `-dev` suffixes and proper plugin installation.

## Installation

```bash
dagger install github.com/SolomonHD/dagger-packer-plugin@v1.0.0
```

## Features

- **Auto-detect plugin name** from directory structure (e.g., `packer-plugin-docker` → `docker`)
- **Automatic lowercase normalization**: Plugin identifiers are normalized to lowercase per HashiCorp requirements
- **Go version auto-detection**: Reads `.go-version` file when `--go-version` not provided
- **Version detection**: Identify if plugin uses VERSION file, hardcoded version, or ldflags pattern
- **VERSION file support**: Use existing VERSION file as authoritative version source
- **Override any pattern**: Use ldflags to override version regardless of how plugin manages it
- **Support any git hosting**: GitHub, GitLab, private servers
- **Containerized operations**: Reproducible builds using official Go and Packer images
- **Cache-busting**: Binary files are exported on every run, even with identical inputs

## Usage

> **Note:** These examples assume you've installed the module using `dagger install`. If you're developing locally within this repository, omit the `-m dagger-packer-plugin` flag.

### Basic Build and Install

Build a plugin and install it in one command:

```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --version=1.0.10 \
  export --path=.
```

### Using VERSION File

If your plugin has a VERSION file, you can use it as the authoritative version:

```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --use-version-file \
  export --path=.
```

### Detect Version Configuration

Analyze a plugin to see how it manages version information:

```bash
dagger call -m dagger-packer-plugin detect-version \
  --source=./packer-plugin-docker
```

Example output:
```json
{
  "version_source": "file",
  "version_file": "version/VERSION",
  "current_version": "1.0.10",
  "version_package": "github.com/hashicorp/packer-plugin-docker/version",
  "recommendation": "use_version_file"
}
```

### Build Plugin Only

Build without installing (returns container with binary, export to retrieve artifacts):

```bash
dagger call -m dagger-packer-plugin build-plugin \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --version=1.0.10 \
  export --path=.
```

### Update VERSION File Before Build

Update the VERSION file with an explicit version before building:

```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --version=2.0.0 \
  --update-version-file \
  export --path=.
```

### Prepare .gitignore

Add plugin binary to .gitignore (plugin name auto-detected from go.mod):

```bash
dagger call -m dagger-packer-plugin prep-gitignore \
  --source=. \
  export --path=.gitignore
```

With explicit plugin name override:

```bash
dagger call -m dagger-packer-plugin prep-gitignore \
  --source=. \
  --plugin-name=docker \
  export --path=.gitignore
```

### Go Version Auto-Detection

The module automatically detects the Go version from a `.go-version` file in your source directory. This is compatible with common Go version managers like `goenv`, `asdf`, and GitHub Actions.

**Priority order:**
1. Explicit `--go-version` parameter (always takes precedence)
2. `.go-version` file in source directory
3. Default fallback: `1.21`

```bash
# Uses .go-version file if present, otherwise defaults to 1.21
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --version=1.0.10 \
  export --path=.
```

When a `.go-version` file is detected, you'll see:
```
ℹ Using Go 1.23.2 from .go-version file
```

### Custom Go/Packer Versions

Override auto-detected or default versions:

```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/hashicorp/packer-plugin-docker \
  --version=1.0.10 \
  --go-version=1.22 \
  --packer-version=1.10.0 \
  export --path=.
```

> **Note:** Explicit `--go-version` always takes precedence over `.go-version` file detection.

### Private Git Server

Works with any git hosting:

```bash
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-custom \
  --git-source=git.company.internal/team/packer-plugin-custom \
  --version=1.0.0 \
  export --path=.
```

## Parameters

### build-and-install / build-plugin

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--source` | Yes | - | Plugin source directory |
| `--git-source` | Yes | - | Git path (e.g., `github.com/user/plugin`). Auto-normalized to lowercase. |
| `--version` | Conditional | - | Semantic version (required unless `--use-version-file`) |
| `--plugin-name` | No | Auto-detected | Override plugin name. Auto-normalized to lowercase. |
| `--use-version-file` | No | `false` | Use VERSION file for version |
| `--update-version-file` | No | `false` | Update VERSION file before build |
| `--go-version` | No | Auto-detected | Go version. Auto-detected from `.go-version` file, falls back to `1.21` |
| `--packer-version` | No | `latest` | Packer container image version |

### detect-version

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--source` | Yes | Plugin source directory |

### prep-gitignore

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--source` | Yes | - | Plugin source directory containing .gitignore |
| `--plugin-name` | No | Auto-detected | Plugin name override (auto-detected from go.mod). Auto-normalized to lowercase. |

## Automatic Lowercase Normalization

HashiCorp Packer requires plugin source addresses to be fully lowercase for plugin discovery to work correctly. This module automatically normalizes:

- **`--git-source`**: Normalized before use in ldflags and plugin paths
- **`--plugin-name`**: Normalized (whether auto-detected or provided)
- **Binary names**: Always lowercase (e.g., `packer-plugin-docker`)

When normalization changes your input, a warning is displayed:

```
⚠ Warning: git-source normalized to lowercase: github.com/solomonhd/packer-plugin-docker
⚠ Warning: plugin-name normalized to lowercase: docker
```

**Example:**
```bash
# Input with uppercase GitHub username
dagger call -m dagger-packer-plugin build-and-install \
  --source=./packer-plugin-docker \
  --git-source=github.com/SolomonHD/packer-plugin-Docker \
  --version=1.0.0 \
  export --path=.

# Output warnings:
# ⚠ Warning: git-source normalized to lowercase: github.com/solomonhd/packer-plugin-docker
# ⚠ Warning: plugin-name normalized to lowercase: docker
```

If your input is already lowercase, no warning is displayed.

## Version Detection Patterns

The module detects three version management patterns:

1. **VERSION file** (`version_source: "file"`): Plugin uses `//go:embed VERSION` or similar
   - Recommended: Use `--use-version-file` flag
   
2. **Hardcoded** (`version_source: "hardcoded"`): Plugin has `var Version = "1.0.0"` in code
   - Use `--version` to override via ldflags
   
3. **Ldflags** (`version_source: "ldflags"`): Plugin expects version via build flags
   - Must provide `--version` parameter

## Output Structure

After `build-and-install`, you'll have:

```
.
├── packer-plugin-{name}_v{version}_x5.0_{os}_{arch}
└── packer-plugin-{name}_v{version}_x5.0_{os}_{arch}_SHA256SUM
```

These files are ready for Packer to discover and use.

## Development

### Local Development

```bash
# Test functions locally
dagger call detect-version --source=../path/to/plugin

# Run full build
dagger call build-and-install \
  --source=../path/to/plugin \
  --git-source=github.com/user/plugin \
  --version=1.0.0 \
  export --path=/tmp/output
```

### Available Functions

```bash
dagger functions
```

## License

MIT License - See [LICENSE](LICENSE) for details.