#!/usr/bin/env python3
"""Update version in all necessary files"""
import sys
import re
from pathlib import Path


def update_version(new_version: str):
    """Update version in __version__.py and pyproject.toml"""
    project_root = Path(__file__).parent.parent
    
    # Update core/__version__.py
    version_file = project_root / "core" / "__version__.py"
    version_file.write_text(f'"""Version information"""\n__version__ = "{new_version}"\n')
    print(f"✅ Updated core/__version__.py to {new_version}")
    
    # Update pyproject.toml
    pyproject_file = project_root / "pyproject.toml"
    content = pyproject_file.read_text()
    content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        count=1
    )
    pyproject_file.write_text(content)
    print(f"✅ Updated pyproject.toml to {new_version}")
    
    print(f"\n🎉 Version updated to {new_version}")
    print("\nNext steps:")
    print(f"1. Update CHANGELOG.md")
    print(f"2. git add -A")
    print(f"3. git commit -m 'Bump version to {new_version}'")
    print(f"4. git tag v{new_version}")
    print(f"5. git push && git push --tags")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py <new_version>")
        print("Example: python scripts/update_version.py 0.2.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("Version should be in format: X.Y.Z (e.g., 0.2.0)")
        sys.exit(1)
    
    update_version(new_version)
