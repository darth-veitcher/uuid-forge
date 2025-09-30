# Release Process

Comprehensive guide for maintainers on how to prepare, execute, and follow up on UUID-Forge releases.

## Release Overview

UUID-Forge follows [Semantic Versioning](https://semver.org/) and uses an automated release process with proper testing, documentation, and distribution.

### Version Types

- **MAJOR (X.0.0)**: Breaking changes to public API
- **MINOR (X.Y.0)**: New features, backward compatible
- **PATCH (X.Y.Z)**: Bug fixes, backward compatible

## Pre-Release Checklist

### 1. Code Quality Verification

```bash
# Run full test suite
uv run pytest

# Check code coverage
uv run pytest --cov=uuid_forge --cov-report=html
# Ensure coverage is >95%

# Run type checking
uv run mypy src

# Run linting
uv run ruff check src tests

# Format code
uv run black src tests
uv run isort src tests

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### 2. Documentation Updates

```bash
# Build documentation locally
uv run mkdocs build --strict

# Serve documentation for review
uv run mkdocs serve

# Check for broken links
uv run mkdocs build --strict 2>&1 | grep WARNING
```

**Update these files:**
- `CHANGELOG.md` - Add new version entry
- `README.md` - Update examples if needed
- `docs/` - Update any relevant documentation
- `pyproject.toml` - Verify metadata is current

### 3. Version Verification

```bash
# Check current version
uv run python -c "from uuid_forge import __version__; print(__version__)"

# Verify version in all files matches
grep -r "version.*=" pyproject.toml
grep -r "__version__" src/uuid_forge/
```

## Release Preparation

### 1. Update Version Numbers

**pyproject.toml:**
```toml
[project]
version = "1.2.3"
```

**src/uuid_forge/_version.py:**
```python
__version__ = "1.2.3"
```

### 2. Update CHANGELOG.md

```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature descriptions
- New functionality

### Changed
- Modified behavior descriptions
- Updated dependencies

### Fixed
- Bug fix descriptions
- Performance improvements

### Deprecated
- Features marked for removal

### Removed
- Removed features

### Security
- Security improvements
```

### 3. Create Release Branch

```bash
# Create release branch
git checkout -b release/v1.2.3

# Commit version updates
git add .
git commit -m "chore: prepare release v1.2.3"

# Push release branch
git push origin release/v1.2.3
```

## Release Execution

### 1. Final Testing

```bash
# Install in clean environment
python -m venv test-release
source test-release/bin/activate
pip install .

# Test CLI functionality
uuid-forge --version
uuid-forge generate "test-release"

# Test Python API
python -c "from uuid_forge import UUIDGenerator; print(UUIDGenerator().generate('test'))"

# Deactivate test environment
deactivate
rm -rf test-release
```

### 2. Create Release PR

Create a Pull Request from `release/v1.2.3` to `main`:

**PR Title:** `Release v1.2.3`

**PR Description:**
```markdown
## Release v1.2.3

### Changes
- Summary of major changes
- Link to detailed CHANGELOG.md

### Pre-release Checklist
- [x] All tests passing
- [x] Documentation updated
- [x] Version numbers updated
- [x] CHANGELOG.md updated
- [x] Manual testing completed

### Post-merge Actions
- [ ] Create GitHub release
- [ ] Build and publish to PyPI
- [ ] Update documentation site
- [ ] Announce release
```

### 3. Merge and Tag

After PR approval and merge:

```bash
# Switch to main and pull latest
git checkout main
git pull origin main

# Create and push tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

## Automated Release Pipeline

### GitHub Actions Workflow

**.github/workflows/release.yml:**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev

      - name: Run tests
        run: uv run pytest --cov=uuid_forge

      - name: Build documentation
        run: uv run mkdocs build --strict

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Build package
        run: uv build

      - name: Store build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  publish-pypi:
    needs: build
    runs-on: ubuntu-latest
    environment: release
    steps:
      - uses: actions/checkout@v3

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  github-release:
    needs: [test, build]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
          draft: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  deploy-docs:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev

      - name: Deploy documentation
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          uv run mike deploy --push --update-aliases ${{ github.ref_name }} latest
```

## Manual Release Steps

If automated release fails, follow these manual steps:

### 1. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/

# Build package
uv build

# Verify build
ls -la dist/
# Should see: uuid_forge-1.2.3.tar.gz and uuid_forge-1.2.3-py3-none-any.whl
```

### 2. Test Package

```bash
# Test installation from built package
pip install dist/uuid_forge-1.2.3-py3-none-any.whl

# Test functionality
python -c "from uuid_forge import UUIDGenerator; print('OK')"
uuid-forge --version

# Uninstall test installation
pip uninstall uuid-forge -y
```

### 3. Upload to PyPI

```bash
# Install twine if not available
pip install twine

# Check package
uv run twine check dist/*

# Upload to Test PyPI first
uv run twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ uuid-forge==1.2.3

# If test successful, upload to production PyPI
uv run twine upload dist/*
```

### 4. Create GitHub Release

1. Go to GitHub repository releases page
2. Click "Create a new release"
3. Choose the tag `v1.2.3`
4. Title: `v1.2.3`
5. Description: Copy from CHANGELOG.md
6. Attach built files from `dist/`
7. Click "Publish release"

## Post-Release Tasks

### 1. Update Documentation

```bash
# Deploy documentation with version
uv run mike deploy v1.2.3 latest --update-aliases --push

# Verify documentation is live
open https://yourusername.github.io/uuid-forge/
```

### 2. Verify Package Distribution

```bash
# Test installation from PyPI
pip install uuid-forge==1.2.3

# Verify functionality
python -c "from uuid_forge import __version__; print(__version__)"
uuid-forge --version

# Clean up
pip uninstall uuid-forge -y
```

### 3. Update Development Environment

```bash
# Switch to develop branch
git checkout develop

# Merge main into develop
git merge main

# Push updated develop
git push origin develop

# Clean up release branch
git branch -d release/v1.2.3
git push origin --delete release/v1.2.3
```

### 4. Prepare Next Development

**Update version for development:**
```toml
# pyproject.toml
[project]
version = "1.2.4-dev"
```

```python
# src/uuid_forge/_version.py
__version__ = "1.2.4-dev"
```

```bash
# Commit development version
git add .
git commit -m "chore: bump version to 1.2.4-dev"
git push origin develop
```

## Release Communication

### 1. Announcement Channels

**GitHub Release Notes:** Automatically generated
**PyPI Description:** Updated from README.md
**Documentation:** Updated automatically

### 2. Social Media (Optional)

**Twitter:**
```
🎉 UUID-Forge v1.2.3 is now available!

✨ New features:
- Feature 1
- Feature 2

🐛 Bug fixes and improvements

Install: pip install uuid-forge==1.2.3

#Python #UUID #OpenSource
```

## Emergency Procedures

### Hotfix Release

For critical bugs in production:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/v1.2.4

# Make minimal fix
# Update version to 1.2.4
# Update CHANGELOG.md

# Test thoroughly
uv run pytest

# Create PR to main
# After merge, follow normal release process
```

### Release Rollback

If critical issues are discovered:

```bash
# Remove from PyPI (contact PyPI support)
# Create new patch release with fix
# Update documentation to recommend new version
```

### Failed Release Recovery

If release process fails:

1. **Check CI/CD logs** for specific failure
2. **Fix issue** in code or configuration
3. **Delete failed tag** if necessary:
   ```bash
   git tag -d v1.2.3
   git push origin :refs/tags/v1.2.3
   ```
4. **Create new tag** and retry release

## Release Metrics

Track these metrics for each release:

- **Download counts** from PyPI
- **GitHub release downloads**
- **Documentation page views**
- **Issue reports** post-release
- **Community feedback**

## Security Considerations

### Release Security

- **Sign releases** with GPG keys
- **Verify dependencies** are up to date
- **Scan for vulnerabilities** before release
- **Use secure CI/CD practices**

### Dependency Management

```bash
# Update dependencies before release
uv sync --upgrade

# Check for security vulnerabilities
uv run pip-audit

# Review dependency changes
uv run pip list --outdated
```

## Troubleshooting

### Common Issues

**Version Mismatch:**
- Ensure all files have consistent version numbers
- Check both `pyproject.toml` and `_version.py`

**Build Failures:**
- Clean build directories: `rm -rf dist/ build/`
- Check for missing dependencies
- Verify Python version compatibility

**Upload Failures:**
- Check PyPI credentials
- Verify package name availability
- Ensure proper file permissions

**Documentation Deployment:**
- Check GitHub Pages settings
- Verify mike configuration
- Test documentation build locally

## Next Steps

After successful release:

- Monitor for issues and feedback
- Plan next release features
- Update project roadmap
- Review and improve release process

For more information:
- [Contributing Guidelines](contributing.md)
- [Development Setup](setup.md)
- [Testing Guide](testing.md)
