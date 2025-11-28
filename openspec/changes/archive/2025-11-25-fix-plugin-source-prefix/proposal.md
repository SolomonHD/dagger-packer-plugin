# Change: Fix plugin source prefix for Packer install command

## Why

The `packer plugins install` command requires the plugin source string to NOT include the `packer-plugin-` prefix. Currently, the module passes `git_source` directly (e.g., `github.com/solomonhd/packer-plugin-ansible-navigator`), but Packer expects `github.com/solomonhd/ansible-navigator`. This causes installation failures with the error:

```
Invalid source string "github.com/solomonhd/packer-plugin-ansible-navigator": 
Plugin source has a type with the prefix "packer-plugin-", which isn't valid.
Did you mean "ansible-navigator"?
```

## What Changes

- Add helper function `_strip_plugin_prefix_from_source()` to transform git_source for plugin registration
- Modify `install_plugin()` to use transformed source for `packer plugins install` command
- Modify `install_plugin()` to use transformed source for plugin path retrieval
- ldflags in `build_plugin()` continue using the original (full) git_source path

## Impact

- Affected specs: `install-plugin`
- Affected code: [`main.py:install_plugin()`](dagger/modules/dagger-packer-plugin/.dagger/src/dagger_packer_plugin/main.py:351)
- No breaking changes to function signatures or parameters