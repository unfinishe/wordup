#!/usr/bin/env python3
"""
Script to sync version from pyproject.toml to src/__version__.py
Usage: python scripts/sync_version.py [release_name]
"""

import sys
import os
import re
from datetime import datetime

def read_version_from_pyproject():
    """Read version from pyproject.toml"""
    pyproject_path = "pyproject.toml"
    if not os.path.exists(pyproject_path):
        raise FileNotFoundError("pyproject.toml not found")
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Find version line
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not version_match:
        raise ValueError("Version not found in pyproject.toml")
    
    return version_match.group(1)

def parse_version(version_str):
    """Parse version string to tuple"""
    parts = version_str.split('.')
    return tuple(int(p) for p in parts)

def write_version_file(version, release_name=None):
    """Write version information to src/__version__.py"""
    version_info = parse_version(version)
    build_date = datetime.now().strftime("%Y-%m-%d")
    
    if release_name is None:
        # Generate release name based on version
        major, minor, patch = version_info
        if major == 0:
            release_name = f"Beta {minor}.{patch}" if minor > 0 else "Initial Release"
        else:
            release_name = f"Release {version}"
    
    content = f'''"""Version information for WordUp."""

__version__ = "{version}"
__version_info__ = {version_info}

# Release information
RELEASE_NAME = "{release_name}"
BUILD_DATE = "{build_date}"
'''
    
    os.makedirs("src", exist_ok=True)
    with open("src/__version__.py", 'w') as f:
        f.write(content)
    
    print(f"✅ Updated version to {version} ({release_name})")
    print(f"📅 Build date: {build_date}")

def main():
    try:
        version = read_version_from_pyproject()
        release_name = sys.argv[1] if len(sys.argv) > 1 else None
        write_version_file(version, release_name)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()