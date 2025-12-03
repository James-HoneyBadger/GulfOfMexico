# Quick Start for PyPI Publishing

## One-Time Setup

```bash
# Install build tools
pip install --upgrade build twine

# Get API token from https://pypi.org/manage/account/token/
# Create ~/.pypirc with your token (see PYPI_PUBLISHING.md for details)
```

## Publishing Workflow

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md

# 3. Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# 4. Test upload (first time or testing)
python -m twine upload --repository testpypi dist/*

# 5. Verify test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps gulfofmexico
gulfofmexico --help

# 6. Upload to production PyPI
python -m twine upload dist/*

# 7. Verify production
pip install gulfofmexico
gulfofmexico --help
```

## Package Info

- **Name**: gulfofmexico
- **Current Version**: 0.1.1
- **PyPI URL**: https://pypi.org/project/gulfofmexico/
- **Commands installed**:
  - `gulfofmexico` / `gom` - Main interpreter
  - `gomconfig` - Language configuration tool
  - `gom-ide` - Graphical IDE

## Pre-Flight Checklist

- [x] `pyproject.toml` configured with proper metadata
- [x] MIT license specified
- [x] README.md included
- [x] Console scripts defined
- [x] MANIFEST.in created
- [x] Package builds successfully
- [ ] Create PyPI account and API token
- [ ] Test upload to Test PyPI
- [ ] Production upload to PyPI

See [PYPI_PUBLISHING.md](PYPI_PUBLISHING.md) for detailed instructions.
