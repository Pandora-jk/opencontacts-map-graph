#!/bin/bash
# Version bump script for manual version management
# Usage: ./version-bump.sh [major|minor|patch|version]

set -e

VERSION_FILE="app/build.gradle.kts"
CURRENT_VERSION=$(grep -oP 'versionName\s*=\s*"\K[^"]+' "$VERSION_FILE")

echo "Current version: $CURRENT_VERSION"

if [ -z "$CURRENT_VERSION" ]; then
    CURRENT_VERSION="0.0.1"
    echo "No version found, starting at: $CURRENT_VERSION"
fi

MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)

case "$1" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    version)
        if [ -z "$2" ]; then
            echo "Error: version type requires version number"
            exit 1
        fi
        NEW_VERSION="$2"
        echo "Setting version to: $NEW_VERSION"
        sed -i "s/versionName = \"[0-9.]*\"/versionName = \"$NEW_VERSION\"/" "$VERSION_FILE"
        exit 0
        ;;
    *)
        # Default: increment patch
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

sed -i "s/versionName = \"[0-9.]*\"/versionName = \"$NEW_VERSION\"/" "$VERSION_FILE"

echo "Version updated in $VERSION_FILE"
git add "$VERSION_FILE"
git commit -m "chore: bump version to $NEW_VERSION"
