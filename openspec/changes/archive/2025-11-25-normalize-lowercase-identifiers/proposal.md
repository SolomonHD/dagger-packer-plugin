# Change: Normalize Plugin Identifiers to Lowercase

## Why
HashiCorp Packer requires plugin source addresses to be fully lowercase for plugin discovery to work correctly. The current module preserves whatever case is provided in `--git-source` and `--plugin-name` parameters, which can cause plugin registration failures or discovery issues when uppercase characters are used (e.g., GitHub usernames like `SolomonHD`).

## What Changes
- **Normalize `git_source`** to lowercase before use in ldflags, plugin paths, and registration commands
- **Normalize `plugin_name`** (auto-detected or provided) to lowercase before use in binary naming
- **Output warnings** when normalization changes the input, informing users what was normalized
- **Update `_extract_plugin_name`** helper to return lowercase names
- **Binary names** always use lowercase: `packer-plugin-docker` not `packer-plugin-Docker`

## Impact
- Affected specs: `build-plugin`, `install-plugin`, `gitignore-prep`
- Affected code: `.dagger/src/dagger_packer_plugin/main.py`
- Non-breaking: Existing lowercase inputs continue to work without warnings
- README update needed to document automatic normalization behavior