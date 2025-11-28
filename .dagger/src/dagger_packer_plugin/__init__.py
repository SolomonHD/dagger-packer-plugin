"""Dagger module for building and installing HashiCorp Packer plugins.

This module automates the complete Packer plugin build and installation process:
- Detects version management patterns (VERSION file, hardcoded, ldflags)
- Builds plugins with proper ldflags to eliminate -dev suffixes
- Installs plugins using HashiCorp Packer container
- Manages .gitignore entries for plugin binaries

Key features:
- Auto-detect plugin name from directory structure
- Support any git hosting service (GitHub, GitLab, private servers)
- Containerized operations for reproducibility
- Single workflow combining build and install phases
"""

from .main import DaggerPackerPlugin as DaggerPackerPlugin
