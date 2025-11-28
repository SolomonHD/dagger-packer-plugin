"""Dagger module for building and installing HashiCorp Packer plugins.

This module automates the Packer plugin build and installation process,
ensuring reproducible builds without -dev suffixes and proper plugin installation.
"""

import json
import re
import time
from typing import Annotated, Optional

import dagger
from dagger import dag, function, object_type, Doc


# Default Go version when no .go-version file and no explicit --go-version
DEFAULT_GO_VERSION = "1.21"


# Storage for normalization warnings to be included in output
_normalization_warnings: list[str] = []


def _normalize_to_lowercase(value: str) -> tuple[str, bool]:
    """Normalize a string to lowercase.
    
    Args:
        value: String to normalize
        
    Returns:
        Tuple of (normalized_value, was_changed)
    """
    normalized = value.lower()
    was_changed = normalized != value
    return normalized, was_changed


def _log_normalization_warning(param_name: str, original: str, normalized: str) -> str:
    """Generate a warning message for normalization.
    
    Args:
        param_name: Name of the parameter that was normalized
        original: Original value before normalization
        normalized: Value after normalization
        
    Returns:
        Warning message string
    """
    return f"⚠ Warning: {param_name} normalized to lowercase: {normalized}"


def _strip_plugin_prefix_from_source(git_source: str) -> str:
    """Strip `packer-plugin-` prefix from the repository name in git_source.
    
    Packer's `packer plugins install` command expects the source string WITHOUT
    the `packer-plugin-` prefix in the repository name. For example:
    - Input: `github.com/solomonhd/packer-plugin-ansible-navigator`
    - Output: `github.com/solomonhd/ansible-navigator`
    
    The ldflags still need the original git_source (full Go module path).
    
    Args:
        git_source: Full git path (e.g., github.com/user/packer-plugin-example)
        
    Returns:
        Transformed path for `packer plugins install` command
    """
    parts = git_source.rstrip("/").split("/")
    if not parts:
        return git_source
    
    # Check if the final segment starts with `packer-plugin-`
    final_segment = parts[-1]
    if final_segment.startswith("packer-plugin-"):
        # Strip the prefix from the final segment
        stripped_name = final_segment[len("packer-plugin-"):]
        parts[-1] = stripped_name
        return "/".join(parts)
    
    # If no prefix found, return unchanged
    return git_source


async def _detect_go_version(source: dagger.Directory) -> Optional[str]:
    """Detect Go version from .go-version file in source directory.
    
    Args:
        source: Plugin source directory to check for .go-version file
        
    Returns:
        Go version string if .go-version file exists and is valid, None otherwise
    """
    try:
        content = await source.file(".go-version").contents()
        version = content.strip()
        if version:
            return version
        return None
    except Exception:
        # File doesn't exist or can't be read
        return None


async def _resolve_go_version(
    source: dagger.Directory,
    explicit_version: Optional[str],
) -> tuple[str, str]:
    """Resolve the Go version to use based on priority.
    
    Priority order:
    1. Explicit --go-version parameter (if provided and not default sentinel)
    2. .go-version file in source directory
    3. Default fallback (1.21)
    
    Args:
        source: Plugin source directory
        explicit_version: Explicitly provided version (None means use auto-detection)
        
    Returns:
        Tuple of (resolved_version, source_description)
        where source_description is one of: "explicit", "file", "default"
    """
    # If explicit version provided, use it
    if explicit_version is not None:
        return explicit_version, "explicit"
    
    # Try to detect from .go-version file
    detected = await _detect_go_version(source)
    if detected:
        return detected, "file"
    
    # Fall back to default
    return DEFAULT_GO_VERSION, "default"


@object_type
class DaggerPackerPlugin:
    """Automate Packer plugin builds and installations with proper versioning."""

    # ========================================================================
    # Version Detection Capability
    # ========================================================================

    @function
    async def detect_version(
        self,
        source: Annotated[
            dagger.Directory,
            Doc("Plugin source directory (use --source=. for your project)")
        ],
    ) -> str:
        """
        Analyze plugin source code to detect how version information is managed.
        
        Returns JSON report with version_source, version_file, current_version,
        and version_package fields.
        
        Args:
            source: Plugin source directory containing Go code
            
        Returns:
            JSON string with detection results
        """
        report = {
            "version_source": "ldflags",  # default if no file or hardcoded found
            "version_file": None,
            "current_version": None,
            "version_package": None,
            "recommendation": None,
        }
        
        # Check for VERSION file at common locations
        version_locations = ["version/VERSION", "VERSION"]
        for loc in version_locations:
            try:
                content = await source.file(loc).contents()
                version = content.strip()
                if version:
                    report["version_file"] = loc
                    report["current_version"] = version
                    report["version_source"] = "file"
                    break
            except Exception:
                continue
        
        # Check for go:embed pattern in version/version.go
        try:
            version_go_content = await source.file("version/version.go").contents()
            
            # Look for go:embed pattern
            if "//go:embed VERSION" in version_go_content or "//go:embed version/VERSION" in version_go_content:
                if report["version_file"]:
                    report["version_source"] = "file"
                    report["recommendation"] = "use_version_file"
            
            # Extract package path from import or module
            # Try to find the module path from go.mod
            try:
                go_mod_content = await source.file("go.mod").contents()
                module_match = re.search(r'^module\s+(\S+)', go_mod_content, re.MULTILINE)
                if module_match:
                    report["version_package"] = f"{module_match.group(1)}/version"
            except Exception:
                pass
            
            # Look for hardcoded version pattern
            hardcoded_match = re.search(r'var\s+Version\s*=\s*["\']([^"\']+)["\']', version_go_content)
            if hardcoded_match and not report["version_file"]:
                report["version_source"] = "hardcoded"
                report["current_version"] = hardcoded_match.group(1)
            
            # Check for ldflags pattern (var Version string without initialization)
            ldflags_match = re.search(r'var\s+Version\s+string\s*$', version_go_content, re.MULTILINE)
            if ldflags_match and not report["version_file"] and not hardcoded_match:
                report["version_source"] = "ldflags"
                
        except Exception:
            # version/version.go doesn't exist, check root for version.go
            try:
                root_version_go = await source.file("version.go").contents()
                hardcoded_match = re.search(r'var\s+Version\s*=\s*["\']([^"\']+)["\']', root_version_go)
                if hardcoded_match and not report["version_file"]:
                    report["version_source"] = "hardcoded"
                    report["current_version"] = hardcoded_match.group(1)
            except Exception:
                pass
        
        # If we have a VERSION file and detected embed, recommend using it
        if report["version_file"] and report["version_source"] == "file":
            report["recommendation"] = "use_version_file"
        
        return json.dumps(report, indent=2)

    def _validate_version(self, version: str) -> tuple[bool, str]:
        """Validate semantic version format.
        
        Args:
            version: Version string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for v prefix
        if version.startswith("v"):
            return False, f"Version '{version}' should not have 'v' prefix. Use '{version[1:]}' instead."
        
        # Basic semver pattern
        semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$'
        if not re.match(semver_pattern, version):
            return False, f"Version '{version}' is not valid semantic versioning. Use format: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
        
        return True, ""

    def _extract_plugin_name(self, dirname: str) -> tuple[str, bool]:
        """Extract plugin name from directory name, normalized to lowercase.
        
        Args:
            dirname: Directory name to parse
            
        Returns:
            Tuple of (plugin_name, was_normalized) where plugin_name is lowercase
            and was_normalized indicates if the original contained uppercase
        """
        # Strip packer-plugin- prefix if present (case-insensitive check)
        dirname_lower = dirname.lower()
        if dirname_lower.startswith("packer-plugin-"):
            name = dirname[14:]  # len("packer-plugin-") == 14
        else:
            name = dirname
        
        # Normalize to lowercase
        normalized, was_changed = _normalize_to_lowercase(name)
        return normalized, was_changed

    # ========================================================================
    # Build Plugin Capability
    # ========================================================================

    @function
    async def build_plugin(
        self,
        source: Annotated[
            dagger.Directory,
            Doc("Plugin source directory containing Go code (use --source=. for your project)")
        ],
        git_source: Annotated[
            str,
            Doc("Git path for the plugin (e.g., github.com/user/packer-plugin-example). Automatically normalized to lowercase.")
        ],
        version: Annotated[
            Optional[str],
            Doc("Semantic version (e.g., 1.0.10). Required unless use_version_file is true")
        ] = None,
        plugin_name: Annotated[
            Optional[str],
            Doc("Plugin name override (auto-detected from directory name if not provided). Automatically normalized to lowercase.")
        ] = None,
        use_version_file: Annotated[
            bool,
            Doc("Use VERSION file from source as version (default: false)")
        ] = False,
        update_version_file: Annotated[
            bool,
            Doc("Update VERSION file with provided version before build (default: false)")
        ] = False,
        go_version: Annotated[
            Optional[str],
            Doc("Go version for building. Auto-detected from .go-version file if not provided, defaults to 1.21")
        ] = None,
        _skip_normalization: bool = False,
        _resolved_go_version: Optional[str] = None,
    ) -> dagger.Container:
        """
        Build a Packer plugin using Go with proper ldflags.
        
        This function compiles the plugin with ldflags that clear VersionPrerelease
        to avoid -dev suffixes that break Packer's plugin discovery system.
        
        Go version is determined by priority:
        1. Explicit --go-version parameter
        2. .go-version file in source directory
        3. Default fallback (1.21)
        
        Note: git_source and plugin_name are automatically normalized to lowercase
        per HashiCorp Packer's requirements. A warning is output if normalization occurs.
        
        Args:
            source: Plugin source directory
            git_source: Git import path for ldflags
            version: Semantic version string
            plugin_name: Override auto-detected plugin name
            use_version_file: Read version from VERSION file
            update_version_file: Update VERSION file before build
            go_version: Go container image version (auto-detected from .go-version if not provided)
            
        Returns:
            Container with built plugin binary at /work/packer-plugin-{name}
        """
        warnings: list[str] = []
        
        # Normalize git_source to lowercase (unless called from build_and_install with pre-normalized values)
        if not _skip_normalization:
            normalized_git_source, git_source_changed = _normalize_to_lowercase(git_source)
            if git_source_changed:
                warnings.append(_log_normalization_warning("git-source", git_source, normalized_git_source))
            git_source = normalized_git_source
        
        # Resolve Go version (use pre-resolved if provided by build_and_install)
        if _resolved_go_version:
            actual_go_version = _resolved_go_version
        else:
            actual_go_version, version_source = await _resolve_go_version(source, go_version)
            if version_source == "file":
                warnings.append(f"ℹ Using Go {actual_go_version} from .go-version file")
        
        # Detect version info
        detection_json = await self.detect_version(source)
        detection = json.loads(detection_json)
        
        # Determine actual version to use
        actual_version = version
        if use_version_file:
            if detection["version_file"] and detection["current_version"]:
                if not actual_version:
                    actual_version = detection["current_version"]
                # If explicit version provided, it takes precedence
            else:
                if not actual_version:
                    return dag.container().from_("alpine:latest").with_exec([
                        "sh", "-c",
                        "echo '✗ Error: use_version_file is true but no VERSION file found' && exit 1"
                    ])
        
        if not actual_version:
            return dag.container().from_("alpine:latest").with_exec([
                "sh", "-c",
                "echo '✗ Error: version is required. Provide --version or use --use-version-file' && exit 1"
            ])
        
        # Validate version format
        is_valid, error_msg = self._validate_version(actual_version)
        if not is_valid:
            return dag.container().from_("alpine:latest").with_exec([
                "sh", "-c",
                f"echo '✗ Error: {error_msg}' && exit 1"
            ])
        
        # Normalize and auto-detect plugin name
        actual_plugin_name: str
        if plugin_name:
            if not _skip_normalization:
                normalized_name, name_changed = _normalize_to_lowercase(plugin_name)
                if name_changed:
                    warnings.append(_log_normalization_warning("plugin-name", plugin_name, normalized_name))
                actual_plugin_name = normalized_name
            else:
                actual_plugin_name = plugin_name
        else:
            # Auto-detect from git_source path (last segment)
            git_parts = git_source.rstrip("/").split("/")
            dirname = git_parts[-1] if git_parts else "plugin"
            actual_plugin_name, name_changed = self._extract_plugin_name(dirname)
            # Note: warning for auto-detected names is suppressed since they come from normalized git_source
        
        binary_name = f"packer-plugin-{actual_plugin_name}"
        
        # Construct ldflags
        # Always include VersionPrerelease= (empty to avoid -dev)
        # Also set Version if explicitly provided
        ldflags_parts = [
            f"-X {git_source}/version.Version={actual_version}",
            f"-X {git_source}/version.VersionPrerelease=",
        ]
        ldflags = " ".join(ldflags_parts)
        
        # Build the container with cache-busting for consistent exports
        cache_bust = str(int(time.time() * 1000))  # Milliseconds for uniqueness
        build_container = (
            dag.container()
            .from_(f"golang:{actual_go_version}")
            .with_mounted_directory("/work", source)
            .with_workdir("/work")
            .with_env_variable("CGO_ENABLED", "0")
            .with_env_variable("DAGGER_CACHE_BUST", cache_bust)
        )
        
        # Output warnings if any
        if warnings:
            for warning in warnings:
                build_container = build_container.with_exec([
                    "sh", "-c", f"echo '{warning}'"
                ])
        
        # Update VERSION file if requested
        if update_version_file and detection["version_file"]:
            version_file_path = detection["version_file"]
            build_container = build_container.with_exec([
                "sh", "-c", f"echo '{actual_version}' > {version_file_path}"
            ])
        
        # Run go build
        build_container = build_container.with_exec([
            "go", "build",
            f"-ldflags={ldflags}",
            "-o", binary_name,
            ".",
        ])
        
        return build_container

    # ========================================================================
    # Install Plugin Capability
    # ========================================================================

    @function
    async def install_plugin(
        self,
        build_container: Annotated[
            dagger.Container,
            Doc("Container with built plugin binary (from build_plugin)")
        ],
        git_source: Annotated[
            str,
            Doc("Git path for plugin registration (e.g., github.com/user/packer-plugin-example). Automatically normalized to lowercase.")
        ],
        plugin_name: Annotated[
            Optional[str],
            Doc("Plugin name (auto-detected from git_source if not provided). Automatically normalized to lowercase.")
        ] = None,
        packer_version: Annotated[
            str,
            Doc("Packer image version to use (default: latest)")
        ] = "latest",
        _skip_normalization: bool = False,
    ) -> dagger.Directory:
        """
        Install a built Packer plugin using HashiCorp Packer container.
        
        This function runs `packer plugins install` to register the plugin
        and generate checksum files, then returns the installation artifacts.
        
        Note: git_source and plugin_name are automatically normalized to lowercase
        per HashiCorp Packer's requirements. A warning is output if normalization occurs.
        
        Args:
            build_container: Container with built binary from build_plugin
            git_source: Git path for plugin registration
            plugin_name: Plugin name override
            packer_version: Packer container image version
            
        Returns:
            Directory containing installation artifacts (binary + checksum)
        """
        warnings: list[str] = []
        
        # Normalize git_source to lowercase (unless called from build_and_install with pre-normalized values)
        if not _skip_normalization:
            normalized_git_source, git_source_changed = _normalize_to_lowercase(git_source)
            if git_source_changed:
                warnings.append(_log_normalization_warning("git-source", git_source, normalized_git_source))
            git_source = normalized_git_source
        
        # Transform git_source for packer plugins install command
        # Packer expects source string WITHOUT `packer-plugin-` prefix in repo name
        # e.g., github.com/user/ansible-navigator instead of github.com/user/packer-plugin-ansible-navigator
        install_source = _strip_plugin_prefix_from_source(git_source)
        
        # Normalize and auto-detect plugin name
        actual_plugin_name: str
        if plugin_name:
            if not _skip_normalization:
                normalized_name, name_changed = _normalize_to_lowercase(plugin_name)
                if name_changed:
                    warnings.append(_log_normalization_warning("plugin-name", plugin_name, normalized_name))
                actual_plugin_name = normalized_name
            else:
                actual_plugin_name = plugin_name
        else:
            # Auto-detect from git_source path (last segment)
            git_parts = git_source.rstrip("/").split("/")
            dirname = git_parts[-1] if git_parts else "plugin"
            actual_plugin_name, _ = self._extract_plugin_name(dirname)
        
        binary_name = f"packer-plugin-{actual_plugin_name}"
        
        # Get the binary from build container
        built_binary = build_container.file(f"/work/{binary_name}")
        
        # Install using Packer container
        packer_container = (
            dag.container()
            .from_(f"hashicorp/packer:{packer_version}")
            .with_file(f"/{binary_name}", built_binary)
            .with_workdir("/")
        )
        
        # Output warnings if any
        if warnings:
            for warning in warnings:
                packer_container = packer_container.with_exec([
                    "sh", "-c", f"echo '{warning}'"
                ])
        
        # Run packer plugins install with transformed source (without packer-plugin- prefix)
        packer_container = packer_container.with_exec([
            "packer", "plugins", "install",
            "--path", binary_name,
            install_source,
        ])
        
        # Packer stores plugins at /root/.config/packer/plugins/ using the install_source path
        # (the stripped version without packer-plugin- prefix)
        plugin_path = f"/root/.config/packer/plugins/{install_source}"
        
        # Return the directory containing the installed plugins
        return packer_container.directory(plugin_path)

    # ========================================================================
    # Gitignore Prep Capability
    # ========================================================================

    @function
    async def prep_gitignore(
        self,
        source: Annotated[
            dagger.Directory,
            Doc("Plugin source directory containing .gitignore (use --source=. for your project)")
        ],
        plugin_name: Annotated[
            Optional[str],
            Doc("Plugin name override (auto-detected from go.mod if not provided). Automatically normalized to lowercase.")
        ] = None,
    ) -> dagger.File:
        """
        Update .gitignore to exclude Packer plugin build artifacts.
        
        This function reads the existing .gitignore (or creates a new one)
        and adds entries for plugin binaries and checksum files if not already present.
        Plugin name is auto-detected from go.mod module path if not provided.
        
        Patterns added:
        - packer-plugin-{name} (base binary)
        - packer-plugin-{name}_v* (versioned binaries for all OS/arch combinations)
        - *_SHA256SUM (checksum files)
        
        Note: plugin_name is automatically normalized to lowercase
        per HashiCorp Packer's requirements.
        
        Args:
            source: Plugin source directory with existing or new .gitignore
            plugin_name: Plugin name override (without packer-plugin- prefix)
            
        Returns:
            Updated .gitignore file
        """
        warnings: list[str] = []
        actual_plugin_name: Optional[str] = None
        
        # Normalize provided plugin_name or auto-detect
        if plugin_name:
            normalized_name, name_changed = _normalize_to_lowercase(plugin_name)
            if name_changed:
                warnings.append(_log_normalization_warning("plugin-name", plugin_name, normalized_name))
            actual_plugin_name = normalized_name
        else:
            # Auto-detect plugin name from go.mod
            try:
                go_mod_content = await source.file("go.mod").contents()
                module_match = re.search(r'^module\s+(\S+)', go_mod_content, re.MULTILINE)
                if module_match:
                    module_path = module_match.group(1)
                    # Extract the last segment as the repo name
                    dirname = module_path.rstrip("/").split("/")[-1]
                    actual_plugin_name, name_changed = self._extract_plugin_name(dirname)
                    if name_changed:
                        warnings.append(_log_normalization_warning("plugin-name (auto-detected)", dirname, actual_plugin_name))
            except Exception:
                pass
            
            if not actual_plugin_name:
                # Return error if we can't detect plugin name
                return dag.directory().with_new_file(
                    ".gitignore",
                    "# Error: Could not auto-detect plugin name. Please provide --plugin-name\n"
                ).file(".gitignore")
        
        binary_name = f"packer-plugin-{actual_plugin_name}"
        versioned_pattern = f"packer-plugin-{actual_plugin_name}_v*"
        checksum_pattern = "*_SHA256SUM"
        
        # Try to read existing .gitignore
        existing_content = ""
        try:
            existing_content = await source.file(".gitignore").contents()
        except Exception:
            # .gitignore doesn't exist, we'll create it
            pass
        
        # Check which entries already exist (idempotent)
        lines = existing_content.split("\n")
        binary_exists = any(line.strip() == binary_name for line in lines)
        versioned_exists = any(line.strip() == versioned_pattern for line in lines)
        checksum_exists = any(line.strip() == checksum_pattern for line in lines)
        
        # If all entries exist, return unchanged content
        if binary_exists and versioned_exists and checksum_exists:
            return dag.directory().with_new_file(".gitignore", existing_content).file(".gitignore")
        
        # Build new content
        new_content = existing_content.rstrip()
        if new_content and not new_content.endswith("\n"):
            new_content += "\n"
        
        # Add warnings as comments if any
        if warnings:
            new_content += "\n"
            for warning in warnings:
                new_content += f"# {warning}\n"
        
        # Add entries that don't already exist
        entries_to_add: list[str] = []
        if not binary_exists:
            entries_to_add.append(binary_name)
        if not versioned_exists:
            entries_to_add.append(versioned_pattern)
        if not checksum_exists:
            entries_to_add.append(checksum_pattern)
        
        if entries_to_add:
            # Add comment and entries
            if new_content:
                new_content += "\n"
            new_content += "# Packer plugin build artifacts\n"
            for entry in entries_to_add:
                new_content += f"{entry}\n"
        
        return dag.directory().with_new_file(".gitignore", new_content).file(".gitignore")

    # ========================================================================
    # Composite Workflow
    # ========================================================================

    @function
    async def build_and_install(
        self,
        source: Annotated[
            dagger.Directory,
            Doc("Plugin source directory containing Go code (use --source=. for your project)")
        ],
        git_source: Annotated[
            str,
            Doc("Git path for the plugin (e.g., github.com/user/packer-plugin-example). Automatically normalized to lowercase.")
        ],
        version: Annotated[
            Optional[str],
            Doc("Semantic version (e.g., 1.0.10). Required unless use_version_file is true")
        ] = None,
        plugin_name: Annotated[
            Optional[str],
            Doc("Plugin name override (auto-detected from git_source if not provided). Automatically normalized to lowercase.")
        ] = None,
        use_version_file: Annotated[
            bool,
            Doc("Use VERSION file from source as version (default: false)")
        ] = False,
        update_version_file: Annotated[
            bool,
            Doc("Update VERSION file with provided version before build (default: false)")
        ] = False,
        go_version: Annotated[
            Optional[str],
            Doc("Go version for building. Auto-detected from .go-version file if not provided, defaults to 1.21")
        ] = None,
        packer_version: Annotated[
            str,
            Doc("Packer image version for installation (default: latest)")
        ] = "latest",
    ) -> dagger.Directory:
        """
        Build and install a Packer plugin in a single workflow.
        
        This convenience function chains build_plugin and install_plugin,
        returning installation artifacts ready to export.
        
        Go version is determined by priority:
        1. Explicit --go-version parameter
        2. .go-version file in source directory
        3. Default fallback (1.21)
        
        Note: git_source and plugin_name are automatically normalized to lowercase
        per HashiCorp Packer's requirements. A warning is output if normalization occurs.
        
        Args:
            source: Plugin source directory
            git_source: Git import path
            version: Semantic version string
            plugin_name: Override auto-detected plugin name
            use_version_file: Read version from VERSION file
            update_version_file: Update VERSION file before build
            go_version: Go container image version (auto-detected from .go-version if not provided)
            packer_version: Packer container image version
            
        Returns:
            Directory with installation artifacts (binary + checksum)
            
        Example:
            dagger call build-and-install \\
              --source=. \\
              --git-source=github.com/user/packer-plugin-example \\
              --version=1.0.0 \\
              export --path=.
        """
        # Normalize inputs once at the entry point to avoid duplicate warnings
        normalized_git_source, git_source_changed = _normalize_to_lowercase(git_source)
        normalized_plugin_name: Optional[str] = None
        plugin_name_changed = False
        
        if plugin_name:
            normalized_plugin_name, plugin_name_changed = _normalize_to_lowercase(plugin_name)
        
        # Resolve Go version once at entry point
        resolved_go_version, go_version_source = await _resolve_go_version(source, go_version)
        go_version_info: Optional[str] = None
        if go_version_source == "file":
            go_version_info = f"ℹ Using Go {resolved_go_version} from .go-version file"
        
        # Build the plugin (pass normalized and pre-resolved values)
        build_container = await self.build_plugin(
            source=source,
            git_source=normalized_git_source,
            version=version,
            plugin_name=normalized_plugin_name,
            use_version_file=use_version_file,
            update_version_file=update_version_file,
            go_version=None,  # Don't pass explicit, use resolved
            _skip_normalization=True,
            _resolved_go_version=resolved_go_version,
        )
        
        # Add warnings/info to the build container
        if go_version_info:
            build_container = build_container.with_exec(["sh", "-c", f"echo '{go_version_info}'"])
        if git_source_changed:
            warning = _log_normalization_warning("git-source", git_source, normalized_git_source)
            build_container = build_container.with_exec(["sh", "-c", f"echo '{warning}'"])
        if plugin_name_changed:
            warning = _log_normalization_warning("plugin-name", plugin_name, normalized_plugin_name)
            build_container = build_container.with_exec(["sh", "-c", f"echo '{warning}'"])
        
        # Install the plugin (pass normalized values, skip internal normalization)
        return await self.install_plugin(
            build_container=build_container,
            git_source=normalized_git_source,
            plugin_name=normalized_plugin_name,
            packer_version=packer_version,
            _skip_normalization=True,
        )
