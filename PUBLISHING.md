# Publishing to PyPI Guide

Complete guide for publishing Forge to PyPI using GitHub Actions.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Setup Steps](#setup-steps)
- [Publishing](#publishing)
- [Private Repository](#private-repository)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

**For the impatient:**

```bash
# 1. Update pyproject.toml (name, version, author, URLs)
# 2. Test build locally
./scripts/test_build.sh

# 3. Configure PyPI Trusted Publishing at:
#    https://pypi.org/manage/account/publishing/

# 4. Create GitHub environment: Settings → Environments → "pypi"

# 5. Create a GitHub Release → Automatic publish!
```

---

## Prerequisites

### 1. Accounts

- **PyPI Account**: https://pypi.org (for production)
- **Test PyPI Account**: https://test.pypi.org (optional, for testing)

### 2. GitHub Repository

Your code must be in a GitHub repository (public or private).

**Repository Visibility:**

| Type | Pros | Cons |
|------|------|------|
| **Public** | ✅ Unlimited Actions minutes<br>✅ Community contributions<br>✅ Full transparency | ❌ Source code visible |
| **Private** | ✅ Source code private<br>✅ Same publishing process | ⚠️ Limited Actions minutes (2,000/month free)<br>⚠️ Package still public on PyPI |

> **Important**: Packages on PyPI are always public, even from private repos.

### 3. Package Name

Check if your desired name is available:
- Visit: https://pypi.org/project/your-package-name/
- If taken, choose alternatives: `fastapi-forge`, `forge-cli`, etc.

---

## Setup Steps

### Step 1: Update Package Metadata

Edit `pyproject.toml`:

```toml
[project]
name = "ningfastforge"  # ⚠️ Must be unique on PyPI
version = "0.1.0"       # ⚠️ Update for each release
authors = [
    {name = "Ning", email = "ning3739@gmail.com"}  # ⚠️ Update
]

[project.urls]
Homepage = "https://github.com/ning3739/forge"      # ⚠️ Update
Repository = "https://github.com/ning3739/forge"    # ⚠️ Update
Issues = "https://github.com/ning3739/forge/issues" # ⚠️ Update
```

### Step 2: Update LICENSE

Edit `LICENSE` and replace `[Your Name]` with your actual name.

### Step 3: Test Build Locally

```bash
# Run the test script
./scripts/test_build.sh

# Or manually:
pip install build twine
python -m build
twine check dist/*
```

### Step 4: Configure PyPI Trusted Publishing

**Trusted Publishing** is the secure, modern way to publish (no API tokens needed).

#### Visual Guide

```
Your Repository:
├── .github/
│   └── workflows/
│       └── publish.yml  ← Workflow name: "publish.yml"
├── pyproject.toml       ← Package name: "ningfastforge"
└── ...

PyPI Form Fields:
┌─────────────────────────────────────────┐
│ PyPI Project Name: ningfastforge        │ ← from pyproject.toml
│ Owner: yourusername                     │ ← your GitHub username
│ Repository name: forge                  │ ← just repo name
│ Workflow name: publish.yml              │ ← just filename!
│ Environment name: pypi                  │ ← from workflow
└─────────────────────────────────────────┘
```

#### For Production (PyPI):

1. Go to: https://pypi.org/manage/account/publishing/
2. Click **"Add a new pending publisher"**
3. Fill in the form:
   - **PyPI Project Name**: `ningfastforge` (from your `pyproject.toml`)
   - **Owner**: `ning3739` (your GitHub username)
   - **Repository name**: `forge` (just repo name, NOT the full URL)
   - **Workflow name**: `publish.yml` ⚠️ **Just the filename, not the path!**
   - **Environment name**: `pypi` ⚠️ **Must match the workflow file**
4. Click **"Add"**

> **Important**: 
> - Workflow name is just `publish.yml` (not `.github/workflows/publish.yml`)
> - The file must exist at `.github/workflows/publish.yml` in your repo
> - Push the workflow file to GitHub before configuring PyPI

#### Common Errors

| Error | Solution |
|-------|----------|
| "Workflow name not found" | Ensure `.github/workflows/publish.yml` exists and is pushed to GitHub |
| "Environment name mismatch" | Check environment name matches exactly (case-sensitive) |
| "Repository not found" | Use just repo name (e.g., `forge`), not full URL |

#### For Testing (Test PyPI):

Same steps at https://test.pypi.org/manage/account/publishing/ but use:
- **Environment name**: `testpypi` ⚠️ **Must match the workflow file**

### Example Configuration

**For Production PyPI:**
```
PyPI Project Name:    ningfastforge
Owner:                ning3739
Repository name:      forge
Workflow name:        publish.yml
Environment name:     pypi
```

**For Test PyPI:**
```
PyPI Project Name:    ningfastforge
Owner:                ning3739
Repository name:      forge
Workflow name:        publish.yml
Environment name:     testpypi
```

---

## Pre-Publishing Checklist

Use this checklist before publishing:

### Configuration
- [ ] Updated `pyproject.toml` (name, version, author, URLs)
- [ ] Updated `LICENSE` with your name
- [ ] Updated `CHANGELOG.md` with changes

### Testing
- [ ] Tested build locally: `./scripts/test_build.sh`
- [ ] Verified package contents: `tar -tzf dist/*.tar.gz | less`
- [ ] Tested installation: `pip install dist/*.whl && forge --version`

### PyPI Setup
- [ ] Created PyPI account
- [ ] Configured Trusted Publishing with correct values
- [ ] Created GitHub environment: `pypi` or `testpypi`

### Publishing
- [ ] Pushed all changes to GitHub
- [ ] Created GitHub Release (or triggered manual workflow)
- [ ] Verified installation from PyPI: `pip install ningfastforge`

---

### Step 5: Configure GitHub Environment

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Environments**
3. Click **"New environment"**
4. Name it: `pypi` (or `testpypi` for testing)
5. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches

---

## Publishing

### Automated Release Process

**The project uses fully automated CI/CD:**

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.2"
   ```

2. **Update** `CHANGELOG.md` with changes:
   ```markdown
   ## [0.1.2] - 2025-01-06
   
   ### Added
   - New feature
   
   ### Fixed
   - Bug fix
   ```

3. **Commit and push to main**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.2"
   git push origin main
   ```

4. **Automatic process** (no manual steps needed):
   - ✅ CI tests run on Python 3.9-3.13
   - ✅ Package is built and validated
   - ✅ Published to PyPI automatically
   - ✅ Git tag is created automatically
   - ✅ GitHub Release is created with changelog

**That's it!** Just push to main and everything happens automatically.

### Version Management

The workflow automatically:
- Detects version from `pyproject.toml`
- Checks if version already published
- Skips if version tag already exists
- Creates tag and release after successful publish

### Monitoring

Watch the progress:
- **Actions**: https://github.com/ning3739/forge/actions
- **PyPI**: https://pypi.org/project/ningfastforge/
- **Releases**: https://github.com/ning3739/forge/releases

---

## Version Management

Follow **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **PATCH** (0.1.0 → 0.1.1): Bug fixes
- **MINOR** (0.1.0 → 0.2.0): New features (backward compatible)
- **MAJOR** (0.1.0 → 1.0.0): Breaking changes

**Before each release:**

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Commit changes
4. Create release with matching tag

---

## Private Repository

### Using Private Repo with Public PyPI

✅ **Fully supported!** Your setup already works with private repositories.

**What's private:**
- Source code on GitHub
- Git history and commits
- Issues and discussions

**What's public:**
- Package on PyPI (always)
- Package metadata
- Compiled code (can be decompiled)

**GitHub Actions limits for private repos:**
- Free: 2,000 minutes/month
- Pro: 3,000 minutes/month
- Typical usage: ~2-3 minutes per release

### Alternative: Keep Package Private

If you need the package to be private too:

**Option 1: Install from GitHub**
```bash
# Public repo
pip install git+https://github.com/username/forge.git

# Private repo (requires auth)
pip install git+https://github.com/username/forge.git@v0.1.0
```

**Option 2: Private PyPI Server**
- [Gemfury](https://gemfury.com/) - $45/month
- [AWS CodeArtifact](https://aws.amazon.com/codeartifact/)
- [devpi](https://devpi.net/) - Self-hosted, free

---

## Troubleshooting

### Package name already taken

**Error**: Package name exists on PyPI

**Solution**: Choose a different name
- Try: `fastapi-forge`, `forge-cli`, `fastapi-scaffold-cli`
- Update in `pyproject.toml`
- Update in PyPI trusted publisher settings

### Build fails locally

**Error**: Build command fails

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall build tools
pip install --upgrade build twine

# Check for syntax errors
python -m py_compile main.py

# Review error messages in build output
```

### Publishing fails

**Error**: GitHub Actions publish step fails

**Common causes:**

1. **Trusted publisher not configured**
   - Verify settings at PyPI
   - Check environment name matches (`pypi` or `testpypi`)

2. **Package name mismatch**
   - Name in `pyproject.toml` must match PyPI project name
   - Case-sensitive!

3. **Version already exists**
   - Cannot republish same version
   - Increment version number

4. **GitHub environment not created**
   - Create environment in repo settings
   - Name must match workflow (`pypi` or `testpypi`)

### Import errors after installation

**Error**: `ModuleNotFoundError` after `pip install`

**Solution**:
```bash
# Check package structure
tar -tzf dist/*.tar.gz | grep "\.py$"

# Verify packages in pyproject.toml
[tool.setuptools]
packages = ["commands", "core", "ui"]
py-modules = ["main"]

# Rebuild and test
python -m build
pip install dist/*.whl --force-reinstall
```

---

## Adding PyPI Badges to README

After publishing, add these badges to `README.md`:

```markdown
[![PyPI version](https://badge.fury.io/py/ningfastforge.svg)](https://badge.fury.io/py/ningfastforge)
[![Python Versions](https://img.shields.io/pypi/pyversions/ningfastforge.svg)](https://pypi.org/project/ningfastforge/)
[![Downloads](https://pepy.tech/badge/ningfastforge)](https://pepy.tech/project/ningfastforge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

Replace `ningfastforge` with your actual package name.

---

## Checklist

Before publishing:

- [ ] Updated `pyproject.toml` (name, version, author, URLs)
- [ ] Updated `LICENSE` with your name
- [ ] Updated `CHANGELOG.md` with changes
- [ ] Tested build locally: `./scripts/test_build.sh`
- [ ] Configured PyPI trusted publishing
- [ ] Created GitHub environment (`pypi` or `testpypi`)
- [ ] Tested on Test PyPI first (recommended)
- [ ] Created GitHub release with proper tag
- [ ] Verified installation: `pip install ningfastforge`
- [ ] Tested CLI: `forge --version`

---

## Resources

- **PyPI**: https://pypi.org
- **Test PyPI**: https://test.pypi.org
- **Trusted Publishing Guide**: https://docs.pypi.org/trusted-publishers/
- **Python Packaging Guide**: https://packaging.python.org/
- **Semantic Versioning**: https://semver.org/

---

## Need Help?

- Check GitHub Actions logs for detailed error messages
- Review PyPI documentation
- Open an issue in your repository
- Check [Python Packaging Discourse](https://discuss.python.org/c/packaging/)
