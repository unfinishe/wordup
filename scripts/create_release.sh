#!/bin/bash
# Release creation workflow for WordUp
# Usage: ./scripts/create_release.sh <version> [release_name]

set -e

VERSION=$1
RELEASE_NAME=${2:-""}

if [ -z "$VERSION" ]; then
    echo "❌ Usage: $0 <version> [release_name]"
    echo "   Example: $0 1.0.0 'Stable Release'"
    exit 1
fi

echo "🚀 Creating WordUp Release $VERSION"
echo "=================================="

# 1. Update version in pyproject.toml
echo "📝 Updating pyproject.toml..."
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# 2. Sync version to __version__.py
echo "🔄 Syncing version information..."
python3 scripts/sync_version.py "$RELEASE_NAME"

# 3. Run tests
echo "🧪 Running tests..."
if ./scripts/run_tests.sh; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
    read -p "Continue with release anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Release cancelled."
        exit 1
    fi
fi

# 4. Build Docker image
echo "🐳 Building Docker image..."
docker build -t wordup:$VERSION .
docker tag wordup:$VERSION wordup:latest

echo "📦 Docker images created:"
echo "  - wordup:$VERSION"
echo "  - wordup:latest"

# 5. Git operations
echo "📋 Preparing Git commit..."
git add pyproject.toml src/__version__.py

if git diff --cached --quiet; then
    echo "⚠️  No changes to commit"
else
    git commit -m "Release $VERSION: $RELEASE_NAME"
    
    # Create git tag
    echo "🏷️  Creating Git tag..."
    git tag -a "v$VERSION" -m "Release $VERSION: $RELEASE_NAME"
    
    echo "✅ Git tag v$VERSION created"
fi

echo ""
echo "🎉 Release $VERSION prepared successfully!"
echo ""
echo "Next steps:"
echo "1. Update release notes in README.md (manually)"
echo "2. Review changes: git log --oneline -5"
echo "3. Push to repository: git push origin main --tags"
echo "4. Create GitHub release from tag v$VERSION"
echo "5. Push Docker image: docker push wordup:$VERSION"
echo ""