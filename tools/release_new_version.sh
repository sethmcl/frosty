#!/bin/bash
set -e

CWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$(dirname $CWD)"
VERSION=$(cat $ROOT/src/version | xargs)

if [ "$(git rev-parse --abbrev-ref HEAD)" != "master" ]; then
    echo "Please run this command on the master branch."
    exit 1
fi

if [ "$(git status --porcelain)" != "" ]; then
    echo "Please commit all changes before running this command."
    exit 1
fi

echo "Current version is [$VERSION]"
echo -n "New version? "
read NEW_VERSION

if [ "$VERSION" == "$NEW_VERSION" ]; then
    echo "Cannot re-release same version."
    exit 0
fi

echo -n "Release version $NEW_VERSION now? [y/n] "
read CONTINUE

if [ "$CONTINUE" != "y" ]; then
    echo "Aborting release process."
    exit 0
fi

echo $NEW_VERSION > $ROOT/src/version
git add $ROOT/src/version
git commit -m "Release version $NEW_VERSION"
git tag $NEW_VERSION
git tag -d latest
git tag latest
git push origin :refs/tags/latest
git push origin master --tags

