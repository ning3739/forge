#!/bin/bash
# Quick release script

set -e

# Check if version is provided
if [ -z "$1" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.1.1"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🚀 Preparing release $VERSION"

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Check if version is updated in pyproject.toml
if ! grep -q "version = \"$VERSION\"" pyproject.toml; then
    echo "❌ Version $VERSION not found in pyproject.toml"
    echo "Please update version in pyproject.toml first"
    exit 1
fi

# Check if CHANGELOG is updated
if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
    echo "❌ Version $VERSION not found in CHANGELOG.md"
    echo "Please update CHANGELOG.md first"
    exit 1
fi

echo "✅ Version check passed"

# Commit if there are changes
if [ -n "$(git diff --cached)" ]; then
    echo "📝 Committing changes..."
    git commit -m "Bump version to $VERSION"
fi

# Create and push tag
echo "🏷️  Creating tag $TAG..."
git tag -a "$TAG" -m "Release $VERSION"

echo "⬆️  Pushing to GitHub..."
git push origin main
git push origin "$TAG"

echo ""
echo "✅ Release $VERSION initiated!"
echo ""
echo "📋 Next steps:"
echo "  1. Check GitHub Actions: https://github.com/ning3739/forge/actions"
echo "  2. Monitor CI tests"
echo "  3. Wait for automatic PyPI publish"
echo "  4. Verify on PyPI: https://pypi.org/project/ningfastforge/"
echo ""
