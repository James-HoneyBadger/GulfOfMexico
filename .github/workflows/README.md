# Gulf of Mexico — GitHub Actions Workflows

Automated release workflows for the Gulf of Mexico programming language.

## Overview

This directory contains GitHub Actions workflows that automate the release process:

- **`release.yml`** — Primary release workflow using standard GitHub Actions
- **`release_fallback.yml`** — Fallback release workflow with minimal external dependencies

Both workflows are triggered automatically when you push a version tag (e.g., `v0.1.5`) to the repository.

## How Releases Work

### Automatic Release (Tag Push)

1. **Create and push a tag:**
   ```bash
   git tag v0.1.6
   git push origin v0.1.6
   ```

2. **Workflows automatically:**
   - Checkout the tagged commit
   - Set up Python 3.12
   - Build the Python package (wheel + source distribution)
   - Create a GitHub Release with the tag name
   - Attach distribution files to the release
   - Use `CHANGELOG.md` as the release notes

### Manual Release (Workflow Dispatch)

You can also manually trigger a release from the GitHub Actions UI:

1. Go to **Actions** → **Release** (or **Release (Fallback)**)
2. Click **Run workflow**
3. Enter the tag name (e.g., `v0.1.6`)
4. Click **Run workflow**

This is useful for re-running failed releases or creating releases for existing tags.

## Configuration

### PyPI Publishing (Optional)

PyPI publishing is controlled by a repository variable:

- **Enable:** Create a repository variable named `ENABLE_PYPI_PUBLISH` with value `true`
- **Disable:** Delete the variable or set it to `false`

If enabled, you also need to set the `PYPI_API_TOKEN` secret with your PyPI API token.

**To configure:**

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Under **Variables**, add `ENABLE_PYPI_PUBLISH` = `true`
3. Under **Secrets**, add `PYPI_API_TOKEN` = `<your-token>`

### Release Notes

The workflow uses `CHANGELOG.md` from the repository root as the release notes. Keep this file updated with each version's changes.

## Workflow Details

### Primary Workflow (`release.yml`)

Uses standard GitHub Actions:
- `actions/checkout@v4` — Code checkout
- `actions/setup-python@v5` — Python environment
- `actions/upload-artifact@v4` — Build artifacts
- `softprops/action-gh-release@v2` — GitHub Release creation
- `pypa/gh-action-pypi-publish@release/v1` — PyPI publishing (optional)

### Fallback Workflow (`release_fallback.yml`)

More robust with minimal external actions:
- Manual git clone and checkout
- Uses `gh` CLI for release creation
- Uses `twine` for PyPI publishing (optional)

Both workflows produce identical results but use different approaches.

## Troubleshooting

### Workflow Not Triggering

- Verify the tag matches the pattern `v*` (e.g., `v0.1.5`, `v1.0.0`)
- Check that the tag was pushed to GitHub: `git push origin <tag-name>`
- View workflow runs at: https://github.com/James-HoneyBadger/GulfOfMexico/actions

### Build Failures

- Check the workflow logs in the Actions tab
- Ensure `pyproject.toml` has the correct version number
- Verify all dependencies are properly specified

### Release Already Exists

If a release already exists for a tag:
- Delete the release in GitHub UI
- Re-run the workflow manually via workflow dispatch

## Example Release Process

Complete example for releasing v0.1.6:

```bash
# 1. Update version in pyproject.toml
sed -i 's/version = "0.1.5"/version = "0.1.6"/' pyproject.toml

# 2. Update CHANGELOG.md with v0.1.6 changes
# (edit manually)

# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "v0.1.6 - <brief description>"
git push

# 4. Create and push tag
git tag v0.1.6
git push origin v0.1.6

# 5. Wait ~30 seconds, then verify
gh release view v0.1.6
```

The automated workflow will handle the rest!

## Permissions

The workflows require the following permissions (already configured):
- `contents: write` — Create releases and upload assets

These are set in the workflow files and should not need modification.
