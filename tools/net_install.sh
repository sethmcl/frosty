#!/bin/sh
set -e

# VERSION may be specified as an environment variable
# If it is not specified, use default version.
if [ "$VERSION" == "" ]; then
    VERSION=latest
fi

# INSTALL_DIR may be specified as an environment variable
# If it is not specified, use default install location.
if [ "$INSTALL_DIR" == "" ]; then
    INSTALL_DIR="$HOME/.frosty"
fi

# URL to fetch source code from
TAR_URL=https://github.com/sethmcl/frosty/tarball/$VERSION

# Ensure install directory exists, with cache and cli sub directories.
# The frosty source code will be installed in $INSTALL_DIR/cli, and
# frosty will use $INSTALL_DIR/cache to cache modules by default.
# If cli directory exists, delete (overwrite) with new frosty source code.
if [ -d "$INSTALL_DIR/cli" ]; then
    rm -rf "$INSTALL_DIR/cli"
fi

mkdir -p "$INSTALL_DIR/cli"
mkdir -p "$INSTALL_DIR/cache"

echo ">> installing frosty [$VERSION] to $INSTALL_DIR/cli..."
echo ">> fetching $TAR_URL"
echo

curl -Ls $TAR_URL | tar xz --strip-components=1 -C "$INSTALL_DIR/cli"

echo ">> install complete"
echo ">> run frosty from $INSTALL_DIR/cli/bin/frosty"
