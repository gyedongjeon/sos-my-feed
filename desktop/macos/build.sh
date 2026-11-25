#!/usr/bin/env bash
# Run from the repository root with the path to a standalone arm64 Python installation.
set -euo pipefail
version=$(node -p "require('./frontend/package.json').version")
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
image="$stage/image"
contents="$image/SOS My Feed.app/Contents"
resources="$contents/Resources"
mkdir -p "$contents/MacOS" "$resources/backend" "$resources/frontend" desktop/release
cp -R "$1" "$resources/python"
cp backend/{articles,desktop,feeds,server}.py "$resources/backend/"
cp -R frontend/dist "$resources/frontend/"
cp LICENSE desktop/assets/icon.icns "$resources/"
sed "s/VERSION/$version/g" desktop/macos/Info.plist > "$contents/Info.plist"
swiftc -target arm64-apple-macos13.0 desktop/macos/main.swift -o "$contents/MacOS/Reader"
codesign --force --deep --sign - "$image/SOS My Feed.app"
codesign --verify --deep --strict "$image/SOS My Feed.app"
python3 desktop/tests/smoke.py "$resources/python/bin/python3.12" "$resources"
ln -s /Applications "$image/Applications"
hdiutil create -ov -format UDZO -fs HFS+ -volname "SOS My Feed" -srcfolder "$image" "desktop/release/SOS-My-Feed-$version-arm64.dmg"
