## 1. Core Normalization Function
- [x] 1.1 Create `_normalize_to_lowercase` helper that normalizes a string to lowercase and returns tuple of (normalized_value, was_changed)
- [x] 1.2 Create `_log_normalization_warning` helper to output warning message when normalization occurs

## 2. Update build_plugin Function
- [x] 2.1 Normalize `git_source` to lowercase before use in ldflags construction
- [x] 2.2 Output warning if `git_source` was normalized
- [x] 2.3 Ensure `plugin_name` (auto-detected or provided) is normalized to lowercase
- [x] 2.4 Output warning if `plugin_name` was normalized
- [x] 2.5 Verify binary name uses lowercase plugin name

## 3. Update install_plugin Function
- [x] 3.1 Normalize `git_source` to lowercase before use in plugin registration
- [x] 3.2 Output warning if `git_source` was normalized
- [x] 3.3 Normalize `plugin_name` to lowercase before use in binary name
- [x] 3.4 Output warning if `plugin_name` was normalized
- [x] 3.5 Ensure plugin path uses lowercase git_source

## 4. Update prep_gitignore Function
- [x] 4.1 Normalize extracted plugin name (from go.mod) to lowercase
- [x] 4.2 Normalize user-provided `plugin_name` to lowercase
- [x] 4.3 Output warning if normalization occurred
- [x] 4.4 Verify gitignore entry uses lowercase binary name

## 5. Update _extract_plugin_name Helper
- [x] 5.1 Modify `_extract_plugin_name` to return lowercase result
- [x] 5.2 Keep track of whether input contained uppercase for warning purposes

## 6. Update build_and_install Function
- [x] 6.1 Ensure normalized values are passed through consistently to build_plugin and install_plugin
- [x] 6.2 Avoid duplicate warnings (normalize once, pass through)

## 7. Testing
- [x] 7.1 Add unit tests for `_normalize_to_lowercase` helper
- [x] 7.2 Add test case: uppercase git_source is normalized with warning
- [x] 7.3 Add test case: uppercase plugin_name is normalized with warning
- [x] 7.4 Add test case: already lowercase input produces no warning
- [x] 7.5 Add test case: mixed case GitHub username normalizes correctly

## 8. Documentation
- [x] 8.1 Update README to document automatic lowercase normalization
- [x] 8.2 Add example showing warning output when normalization occurs