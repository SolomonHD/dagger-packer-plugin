## 1. Implementation

- [x] 1.1 Update `prep_gitignore` function in `main.py` to add versioned binary pattern (`packer-plugin-{name}_v*`)
- [x] 1.2 Update `prep_gitignore` function to add SHA256SUM pattern (`*_SHA256SUM`)
- [x] 1.3 Implement idempotent checking for each pattern (base binary, versioned, checksum)
- [x] 1.4 Ensure preserved comment structure for new entries

## 2. Documentation

- [x] 2.1 Update README.md `build-plugin` example to include `export --path=.`

## 3. Testing

- [x] 3.1 Add/update unit tests for versioned binary pattern generation
- [x] 3.2 Add/update unit tests for SHA256SUM pattern generation
- [x] 3.3 Add/update unit tests for idempotent pattern checking
- [x] 3.4 Verify existing tests still pass (55 tests passed)

## 4. Validation

- [x] 4.1 Test `prep-gitignore` function with sample plugin (validated via `dagger call prep-gitignore --source=./tests/fixtures/version-file-plugin`)
- [x] 4.2 Verify generated patterns match actual build artifacts (output shows all 3 patterns: base, versioned, checksum)
- [x] 4.3 Verify README example works correctly with `export --path=.`