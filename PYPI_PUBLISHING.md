# PyPI Publishing Guide

## Prerequisites

1. Install build tools:
```bash
pip install --upgrade build twine
```

2. Create PyPI account:
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

3. Configure API token (recommended):
```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
EOF
chmod 600 ~/.pypirc
```

## Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build

# This creates:
# - dist/gulfofmexico-0.1.1.tar.gz (source)
# - dist/gulfofmexico-0.1.1-py3-none-any.whl (wheel)
```

## Test Upload (Recommended First)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps gulfofmexico

# Test it works
gulfofmexico --help
python -m gulfofmexico
```

## Production Upload

```bash
# Upload to PyPI
python -m twine upload dist/*

# Or with explicit repository
python -m twine upload --repository pypi dist/*
```

## Post-Upload Verification

```bash
# Install from PyPI
pip install gulfofmexico

# Verify commands work
gulfofmexico --help
gom --help
gomconfig --help
gom-ide

# Run test program
echo 'print("Hello from PyPI!")!' > test.gom
gulfofmexico test.gom
```

## Version Management

Update version in `pyproject.toml`:
```toml
[tool.poetry]
version = "0.1.2"  # Increment for new releases
```

Follow semantic versioning:
- MAJOR.MINOR.PATCH (e.g., 0.1.1 → 0.1.2)
- 0.x.x = Alpha/Beta (current stage)
- 1.0.0 = First stable release

## Publishing Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Test locally: `pip install -e .`
- [ ] Run tests: `python -m pytest` (if available)
- [ ] Clean build: `rm -rf dist/ build/ *.egg-info`
- [ ] Build: `python -m build`
- [ ] Test upload to Test PyPI
- [ ] Verify test installation works
- [ ] Upload to production PyPI
- [ ] Verify production installation
- [ ] Create git tag: `git tag v0.1.1`
- [ ] Push tag: `git push --tags`

## Troubleshooting

### Missing files in distribution
Add to `MANIFEST.in` or ensure files are tracked by git.

### Import errors after installation
Check package structure and `__init__.py` files.

### Command not found after install
Verify `[tool.poetry.scripts]` in `pyproject.toml`.

### Version already exists
Increment version number - PyPI doesn't allow re-uploads.

## Useful Commands

```bash
# Check package metadata
python -m build --sdist
tar tzf dist/gulfofmexico-*.tar.gz | head -20

# Validate package
python -m twine check dist/*

# View package info
pip show gulfofmexico

# Uninstall
pip uninstall gulfofmexico
```

## Resources

- PyPI: https://pypi.org/project/gulfofmexico/
- Test PyPI: https://test.pypi.org/project/gulfofmexico/
- Packaging Guide: https://packaging.python.org/
- Poetry Docs: https://python-poetry.org/docs/
