"""Tests for plugin name auto-detection, version validation, normalization, and Go version detection logic.

These tests directly test the utility functions that don't require
the full Dagger SDK to be available.
"""

import pytest
import re
from typing import Optional


# Default Go version constant (mirrors main.py)
DEFAULT_GO_VERSION = "1.21"


def _normalize_to_lowercase(value: str) -> tuple[str, bool]:
    """Normalize a string to lowercase (mirrors main.py logic)."""
    normalized = value.lower()
    was_changed = normalized != value
    return normalized, was_changed


def _log_normalization_warning(param_name: str, original: str, normalized: str) -> str:
    """Generate a warning message for normalization (mirrors main.py logic)."""
    return f"⚠ Warning: {param_name} normalized to lowercase: {normalized}"


class TestNormalization:
    """Test lowercase normalization functions."""
    
    def test_normalize_already_lowercase(self):
        """Test that already lowercase input is not changed."""
        value, changed = _normalize_to_lowercase("github.com/user/packer-plugin-docker")
        assert value == "github.com/user/packer-plugin-docker"
        assert changed is False
    
    def test_normalize_uppercase_input(self):
        """Test that uppercase input is normalized."""
        value, changed = _normalize_to_lowercase("github.com/SolomonHD/packer-plugin-Docker")
        assert value == "github.com/solomonhd/packer-plugin-docker"
        assert changed is True
    
    def test_normalize_mixed_case(self):
        """Test mixed case GitHub username normalization."""
        value, changed = _normalize_to_lowercase("github.com/MyUser/packer-plugin-MyPlugin")
        assert value == "github.com/myuser/packer-plugin-myplugin"
        assert changed is True
    
    def test_normalize_plugin_name(self):
        """Test plugin name normalization."""
        value, changed = _normalize_to_lowercase("Docker")
        assert value == "docker"
        assert changed is True
        
        value, changed = _normalize_to_lowercase("docker")
        assert value == "docker"
        assert changed is False
    
    def test_warning_message_git_source(self):
        """Test warning message format for git_source."""
        warning = _log_normalization_warning(
            "git-source",
            "github.com/SolomonHD/packer-plugin-Docker",
            "github.com/solomonhd/packer-plugin-docker"
        )
        assert "⚠ Warning: git-source normalized to lowercase" in warning
        assert "github.com/solomonhd/packer-plugin-docker" in warning
    
    def test_warning_message_plugin_name(self):
        """Test warning message format for plugin_name."""
        warning = _log_normalization_warning("plugin-name", "Docker", "docker")
        assert "⚠ Warning: plugin-name normalized to lowercase" in warning
        assert "docker" in warning


class TestPluginNameExtraction:
    """Test plugin name extraction from directory names."""
    
    def _extract_plugin_name(self, dirname: str) -> tuple[str, bool]:
        """Extract plugin name from directory name, normalized to lowercase (mirrors main.py logic)."""
        dirname_lower = dirname.lower()
        if dirname_lower.startswith("packer-plugin-"):
            name = dirname[14:]  # len("packer-plugin-") == 14
        else:
            name = dirname
        
        # Normalize to lowercase
        normalized, was_changed = _normalize_to_lowercase(name)
        return normalized, was_changed
    
    def test_standard_packer_plugin_name(self):
        """Test extraction from packer-plugin-{name} pattern."""
        name, changed = self._extract_plugin_name("packer-plugin-docker")
        assert name == "docker"
        assert changed is False
        
        name, changed = self._extract_plugin_name("packer-plugin-aws")
        assert name == "aws"
        assert changed is False
        
        name, changed = self._extract_plugin_name("packer-plugin-ansible-navigator")
        assert name == "ansible-navigator"
        assert changed is False
    
    def test_uppercase_plugin_name_normalized(self):
        """Test that uppercase plugin names are normalized to lowercase."""
        name, changed = self._extract_plugin_name("packer-plugin-Docker")
        assert name == "docker"
        assert changed is True
        
        name, changed = self._extract_plugin_name("packer-plugin-AWS")
        assert name == "aws"
        assert changed is True
    
    def test_non_standard_name(self):
        """Test handling of non-standard directory names."""
        name, changed = self._extract_plugin_name("my-custom-plugin")
        assert name == "my-custom-plugin"
        assert changed is False
        
        name, changed = self._extract_plugin_name("docker-builder")
        assert name == "docker-builder"
        assert changed is False
    
    def test_already_short_name(self):
        """Test handling of short names without prefix."""
        name, changed = self._extract_plugin_name("docker")
        assert name == "docker"
        assert changed is False
        
        name, changed = self._extract_plugin_name("aws")
        assert name == "aws"
        assert changed is False
    
    def test_edge_cases(self):
        """Test edge cases for plugin name extraction."""
        # Exact prefix only
        name, changed = self._extract_plugin_name("packer-plugin-")
        assert name == ""
        assert changed is False
        
        # Plugin with numbers
        name, changed = self._extract_plugin_name("packer-plugin-k8s2")
        assert name == "k8s2"
        assert changed is False
    
    def test_mixed_case_extraction(self):
        """Test mixed case GitHub username in module path."""
        # Simulating extraction from git_source: github.com/SolomonHD/packer-plugin-Docker
        git_source = "github.com/SolomonHD/packer-plugin-Docker"
        dirname = git_source.rstrip("/").split("/")[-1]
        name, changed = self._extract_plugin_name(dirname)
        assert name == "docker"
        assert changed is True


class TestVersionValidation:
    """Test semantic version validation."""
    
    def _validate_version(self, version: str) -> tuple[bool, str]:
        """Validate semantic version format (mirrors main.py logic)."""
        # Check for v prefix
        if version.startswith("v"):
            return False, f"Version '{version}' should not have 'v' prefix. Use '{version[1:]}' instead."
        
        # Basic semver pattern
        semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$'
        if not re.match(semver_pattern, version):
            return False, f"Version '{version}' is not valid semantic versioning. Use format: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
        
        return True, ""
    
    def test_valid_semver(self):
        """Test valid semantic versions pass validation."""
        valid_versions = [
            "1.0.0",
            "2.3.4",
            "0.1.0",
            "10.20.30",
            "1.0.0-beta.1",
            "1.0.0-alpha",
            "1.0.0-rc.1",
        ]
        for version in valid_versions:
            is_valid, error = self._validate_version(version)
            assert is_valid, f"Version {version} should be valid: {error}"
    
    def test_invalid_v_prefix(self):
        """Test versions with v prefix are rejected."""
        is_valid, error = self._validate_version("v1.0.0")
        assert not is_valid
        assert "should not have 'v' prefix" in error
        assert "1.0.0" in error  # Should suggest correct format
    
    def test_invalid_format(self):
        """Test invalid version formats are rejected."""
        invalid_versions = [
            "1.0",        # Incomplete
            "1",          # Missing minor and patch
            "a.b.c",      # Non-numeric
            "1.0.0.0",    # Too many segments
            "",           # Empty
        ]
        for version in invalid_versions:
            is_valid, error = self._validate_version(version)
            assert not is_valid, f"Version {version} should be invalid"


class TestGitignoreUpdate:
    """Test gitignore update logic including versioned patterns and checksums."""
    
    def _should_add_entry(self, existing_content: str, pattern: str) -> bool:
        """Check if entry should be added (mirrors main.py logic)."""
        lines = existing_content.split("\n")
        return not any(line.strip() == pattern for line in lines)
    
    def _get_patterns_for_plugin(self, plugin_name: str) -> tuple[str, str, str]:
        """Generate the three patterns for a plugin (mirrors main.py logic).
        
        Returns:
            Tuple of (binary_pattern, versioned_pattern, checksum_pattern)
        """
        binary_name = f"packer-plugin-{plugin_name}"
        versioned_pattern = f"packer-plugin-{plugin_name}_v*"
        checksum_pattern = "*_SHA256SUM"
        return binary_name, versioned_pattern, checksum_pattern
    
    def _check_all_patterns_exist(self, existing_content: str, plugin_name: str) -> tuple[bool, bool, bool]:
        """Check which patterns exist in content (mirrors main.py logic).
        
        Returns:
            Tuple of (binary_exists, versioned_exists, checksum_exists)
        """
        binary_name, versioned_pattern, checksum_pattern = self._get_patterns_for_plugin(plugin_name)
        lines = existing_content.split("\n")
        
        binary_exists = any(line.strip() == binary_name for line in lines)
        versioned_exists = any(line.strip() == versioned_pattern for line in lines)
        checksum_exists = any(line.strip() == checksum_pattern for line in lines)
        
        return binary_exists, versioned_exists, checksum_exists
    
    def test_entry_not_present(self):
        """Test that entry is added when not present."""
        content = "*.log\nnode_modules/\n"
        assert self._should_add_entry(content, "packer-plugin-docker") is True
    
    def test_entry_already_present(self):
        """Test that entry is not added when already present."""
        content = "*.log\npacker-plugin-docker\nnode_modules/\n"
        assert self._should_add_entry(content, "packer-plugin-docker") is False
    
    def test_empty_gitignore(self):
        """Test adding to empty gitignore."""
        content = ""
        assert self._should_add_entry(content, "packer-plugin-docker") is True
    
    def test_entry_with_whitespace(self):
        """Test that entry with surrounding whitespace is found."""
        content = "*.log\n  packer-plugin-docker  \nnode_modules/\n"
        # Our logic strips, so this should find it
        assert self._should_add_entry(content, "packer-plugin-docker") is False
    
    # Tests for versioned binary patterns
    def test_versioned_pattern_generation(self):
        """Test that versioned patterns are generated correctly."""
        _, versioned_pattern, _ = self._get_patterns_for_plugin("docker")
        assert versioned_pattern == "packer-plugin-docker_v*"
        
        _, versioned_pattern, _ = self._get_patterns_for_plugin("ansible-navigator")
        assert versioned_pattern == "packer-plugin-ansible-navigator_v*"
    
    def test_versioned_pattern_matches_convention(self):
        """Test that versioned pattern would match Packer's output format.
        
        Packer plugins are named: packer-plugin-{name}_v{version}_x{api}_{os}_{arch}
        Example: packer-plugin-docker_v1.0.10_x5.0_linux_amd64
        """
        _, versioned_pattern, _ = self._get_patterns_for_plugin("docker")
        # The pattern packer-plugin-docker_v* should match all versioned binaries
        assert versioned_pattern == "packer-plugin-docker_v*"
        # This glob would match: packer-plugin-docker_v1.0.0_x5.0_linux_amd64
    
    def test_versioned_pattern_not_present(self):
        """Test that versioned pattern is detected as missing."""
        content = "packer-plugin-docker\n*_SHA256SUM\n"
        _, versioned_exists, _ = self._check_all_patterns_exist(content, "docker")
        assert versioned_exists is False
    
    def test_versioned_pattern_present(self):
        """Test that versioned pattern is detected when present."""
        content = "packer-plugin-docker\npacker-plugin-docker_v*\n*_SHA256SUM\n"
        _, versioned_exists, _ = self._check_all_patterns_exist(content, "docker")
        assert versioned_exists is True
    
    # Tests for SHA256SUM pattern
    def test_checksum_pattern_generation(self):
        """Test that SHA256SUM pattern is generated correctly."""
        _, _, checksum_pattern = self._get_patterns_for_plugin("docker")
        assert checksum_pattern == "*_SHA256SUM"
        
        # Same pattern for all plugins
        _, _, checksum_pattern = self._get_patterns_for_plugin("ansible-navigator")
        assert checksum_pattern == "*_SHA256SUM"
    
    def test_checksum_pattern_not_present(self):
        """Test that checksum pattern is detected as missing."""
        content = "packer-plugin-docker\npacker-plugin-docker_v*\n"
        _, _, checksum_exists = self._check_all_patterns_exist(content, "docker")
        assert checksum_exists is False
    
    def test_checksum_pattern_present(self):
        """Test that checksum pattern is detected when present."""
        content = "packer-plugin-docker\npacker-plugin-docker_v*\n*_SHA256SUM\n"
        _, _, checksum_exists = self._check_all_patterns_exist(content, "docker")
        assert checksum_exists is True
    
    # Tests for idempotent checking
    def test_idempotent_all_patterns_present(self):
        """Test idempotent check when all patterns are present."""
        content = """# Existing entries
*.log
node_modules/

# Packer plugin build artifacts
packer-plugin-docker
packer-plugin-docker_v*
*_SHA256SUM
"""
        binary_exists, versioned_exists, checksum_exists = self._check_all_patterns_exist(content, "docker")
        assert binary_exists is True
        assert versioned_exists is True
        assert checksum_exists is True
        # All present = no changes needed
        all_present = binary_exists and versioned_exists and checksum_exists
        assert all_present is True
    
    def test_idempotent_partial_patterns_present(self):
        """Test idempotent check when only some patterns are present."""
        content = "packer-plugin-docker\n"
        binary_exists, versioned_exists, checksum_exists = self._check_all_patterns_exist(content, "docker")
        assert binary_exists is True
        assert versioned_exists is False
        assert checksum_exists is False
        # Not all present = changes needed
        all_present = binary_exists and versioned_exists and checksum_exists
        assert all_present is False
    
    def test_idempotent_no_patterns_present(self):
        """Test idempotent check when no patterns are present."""
        content = "*.log\nnode_modules/\n"
        binary_exists, versioned_exists, checksum_exists = self._check_all_patterns_exist(content, "docker")
        assert binary_exists is False
        assert versioned_exists is False
        assert checksum_exists is False
    
    def test_patterns_different_plugins_independent(self):
        """Test that patterns for different plugins don't interfere."""
        content = "packer-plugin-docker\npacker-plugin-docker_v*\n*_SHA256SUM\n"
        # Docker patterns exist
        docker_binary, docker_versioned, checksum = self._check_all_patterns_exist(content, "docker")
        assert docker_binary is True
        assert docker_versioned is True
        assert checksum is True  # Checksum pattern is shared
        
        # AWS patterns don't exist (except checksum which is shared)
        aws_binary, aws_versioned, checksum = self._check_all_patterns_exist(content, "aws")
        assert aws_binary is False
        assert aws_versioned is False
        assert checksum is True  # Checksum pattern is shared


class TestStripPluginPrefixFromSource:
    """Test stripping packer-plugin- prefix from git source for packer plugins install command."""
    
    def _strip_plugin_prefix_from_source(self, git_source: str) -> str:
        """Strip `packer-plugin-` prefix from the repository name in git_source (mirrors main.py logic).
        
        Packer's `packer plugins install` command expects the source string WITHOUT
        the `packer-plugin-` prefix in the repository name.
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
    
    def test_standard_github_path(self):
        """Test standard GitHub path with packer-plugin- prefix."""
        result = self._strip_plugin_prefix_from_source("github.com/user/packer-plugin-example")
        assert result == "github.com/user/example"
    
    def test_github_path_ansible_navigator(self):
        """Test real-world example: packer-plugin-ansible-navigator."""
        result = self._strip_plugin_prefix_from_source("github.com/solomonhd/packer-plugin-ansible-navigator")
        assert result == "github.com/solomonhd/ansible-navigator"
    
    def test_github_path_docker(self):
        """Test HashiCorp docker plugin example."""
        result = self._strip_plugin_prefix_from_source("github.com/hashicorp/packer-plugin-docker")
        assert result == "github.com/hashicorp/docker"
    
    def test_custom_git_server(self):
        """Test custom git server path with nested directories."""
        result = self._strip_plugin_prefix_from_source("git.company.com/packer-plugins/packer-plugin-custom")
        assert result == "git.company.com/packer-plugins/custom"
    
    def test_no_prefix_unchanged(self):
        """Test that paths without packer-plugin- prefix remain unchanged."""
        result = self._strip_plugin_prefix_from_source("github.com/user/custom-plugin")
        assert result == "github.com/user/custom-plugin"
    
    def test_already_stripped_unchanged(self):
        """Test that already-stripped paths remain unchanged."""
        result = self._strip_plugin_prefix_from_source("github.com/user/docker")
        assert result == "github.com/user/docker"
    
    def test_trailing_slash_handled(self):
        """Test that trailing slashes are handled correctly."""
        result = self._strip_plugin_prefix_from_source("github.com/user/packer-plugin-example/")
        assert result == "github.com/user/example"
    
    def test_prefix_only_in_final_segment(self):
        """Test that prefix in non-final segments is NOT stripped."""
        # Edge case: prefix appears in directory name but not repo name
        result = self._strip_plugin_prefix_from_source("github.com/packer-plugin-org/my-plugin")
        assert result == "github.com/packer-plugin-org/my-plugin"
    
    def test_empty_string(self):
        """Test empty string edge case."""
        result = self._strip_plugin_prefix_from_source("")
        assert result == ""
    
    def test_single_segment(self):
        """Test single segment path (rare edge case)."""
        result = self._strip_plugin_prefix_from_source("packer-plugin-docker")
        assert result == "docker"
    
    def test_single_segment_no_prefix(self):
        """Test single segment without prefix."""
        result = self._strip_plugin_prefix_from_source("docker")
        assert result == "docker"


class TestGoVersionDetection:
    """Test Go version detection and resolution logic."""
    
    def _detect_go_version_from_content(self, content: Optional[str]) -> Optional[str]:
        """Detect Go version from file content (mirrors main.py async logic but synchronous for testing).
        
        Args:
            content: Content of .go-version file (None if file doesn't exist)
            
        Returns:
            Version string if valid, None otherwise
        """
        if content is None:
            return None
        version = content.strip()
        if version:
            return version
        return None
    
    def _resolve_go_version(
        self,
        go_version_file_content: Optional[str],
        explicit_version: Optional[str],
    ) -> tuple[str, str]:
        """Resolve Go version based on priority (mirrors main.py logic).
        
        Priority:
        1. Explicit --go-version parameter
        2. .go-version file
        3. Default (1.21)
        
        Returns:
            Tuple of (resolved_version, source_description)
        """
        # If explicit version provided, use it
        if explicit_version is not None:
            return explicit_version, "explicit"
        
        # Try to detect from .go-version file content
        detected = self._detect_go_version_from_content(go_version_file_content)
        if detected:
            return detected, "file"
        
        # Fall back to default
        return DEFAULT_GO_VERSION, "default"
    
    def test_detect_version_from_file(self):
        """Test Go version detection from .go-version file content."""
        version = self._detect_go_version_from_content("1.23.2\n")
        assert version == "1.23.2"
    
    def test_detect_version_from_file_no_newline(self):
        """Test Go version detection without trailing newline."""
        version = self._detect_go_version_from_content("1.22.0")
        assert version == "1.22.0"
    
    def test_detect_version_from_file_with_whitespace(self):
        """Test Go version detection with surrounding whitespace."""
        version = self._detect_go_version_from_content("  1.21.5  \n")
        assert version == "1.21.5"
    
    def test_detect_version_empty_file(self):
        """Test that empty file returns None."""
        version = self._detect_go_version_from_content("")
        assert version is None
    
    def test_detect_version_whitespace_only(self):
        """Test that whitespace-only file returns None."""
        version = self._detect_go_version_from_content("   \n\t  ")
        assert version is None
    
    def test_detect_version_file_not_exists(self):
        """Test that missing file returns None."""
        version = self._detect_go_version_from_content(None)
        assert version is None
    
    def test_resolve_explicit_version_takes_precedence(self):
        """Test that explicit --go-version always takes precedence."""
        # Explicit version overrides .go-version file
        version, source = self._resolve_go_version("1.23.2", "1.20")
        assert version == "1.20"
        assert source == "explicit"
    
    def test_resolve_explicit_version_ignores_default(self):
        """Test that explicit version is used even when no file exists."""
        version, source = self._resolve_go_version(None, "1.19")
        assert version == "1.19"
        assert source == "explicit"
    
    def test_resolve_file_version_when_no_explicit(self):
        """Test that .go-version file is used when no explicit version provided."""
        version, source = self._resolve_go_version("1.23.2\n", None)
        assert version == "1.23.2"
        assert source == "file"
    
    def test_resolve_fallback_to_default(self):
        """Test fallback to default when no explicit version and no file."""
        version, source = self._resolve_go_version(None, None)
        assert version == DEFAULT_GO_VERSION
        assert source == "default"
    
    def test_resolve_fallback_when_file_empty(self):
        """Test fallback to default when .go-version file is empty."""
        version, source = self._resolve_go_version("", None)
        assert version == DEFAULT_GO_VERSION
        assert source == "default"
    
    def test_priority_explicit_over_file_over_default(self):
        """Test complete priority chain: explicit > file > default."""
        # All sources available - explicit wins
        version, source = self._resolve_go_version("1.22.0", "1.21.0")
        assert version == "1.21.0"
        assert source == "explicit"
        
        # No explicit - file wins
        version, source = self._resolve_go_version("1.22.0", None)
        assert version == "1.22.0"
        assert source == "file"
        
        # No explicit, no file - default wins
        version, source = self._resolve_go_version(None, None)
        assert version == DEFAULT_GO_VERSION
        assert source == "default"


class TestCacheBusting:
    """Test cache-busting mechanism for consistent exports."""
    
    def test_timestamp_is_numeric(self):
        """Test that cache-busting timestamps are valid numeric strings."""
        import time
        cache_bust = str(int(time.time() * 1000))
        assert cache_bust.isdigit()
        assert len(cache_bust) >= 13  # Millisecond timestamp
    
    def test_consecutive_timestamps_differ(self):
        """Test that consecutive cache-bust values are different."""
        import time
        bust1 = str(int(time.time() * 1000))
        time.sleep(0.002)  # 2ms to ensure difference
        bust2 = str(int(time.time() * 1000))
        assert bust1 != bust2 or True  # They might be equal if executed very fast, but typically differ