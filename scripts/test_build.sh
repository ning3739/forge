#!/bin/bash
# Test build script - Run this before publishing

set -e

echo "🔧 Installing build dependencies..."
pip install --upgrade pip build twine

echo ""
echo "🏗️  Building package..."
python -m build

echo ""
echo "✅ Checking distribution..."
twine check dist/*

echo ""
echo "📦 Package contents:"
tar -tzf dist/*.tar.gz | head -20

echo ""
echo "✨ Build successful!"
echo ""
echo "To test installation locally:"
echo "  pip install dist/*.whl"
echo "  forge --version"
