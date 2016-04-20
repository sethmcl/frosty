Frosty (Node.js)
================

This tool is used to install Npm modules, as specified in a npm-shrinkwrap.json
file. Each module which is installed will be cached, in $HOME/.frosty by default.

Benefits of this tool over vanilla npm:

1. Modules are cached in a fully expanded, post-install state.
2. This tool can be run in a fully offline mode, so that no network requests will take place.

## How to install
The recommended method for installing is to use this one liner:

```
bash <(curl -s https://raw.githubusercontent.com/sethmcl/frosty/latest/tools/net_install.sh)
```

This will install frosty to `~/.frosty`, and you'll be able to launch frosty by running `~/.frosty/cli/bin/frosty`.

There are two installation options available, which you can select by setting environment variables:

```
# Change the directory where frosty is installed.
INSTALL_DIR=~/some/dir bash <(curl -s https://raw.githubusercontent.com/sethmcl/frosty/latest/tools/net_install.sh)

# Change the version of frosty to install
VERSION=0.0.3 bash <(curl -s https://raw.githubusercontent.com/sethmcl/frosty/latest/tools/net_install.sh)

# Change both the install directory and version
INSTALL_DIR=~/some/dir VERSION=0.0.3 bash <(curl -s https://raw.githubusercontent.com/sethmcl/frosty/latest/tools/net_install.sh)
```

If the `VERSION` variable is not set, the last released version of frosty will be installed. This is denoted by the `latest` tag in this repository.

## Usage
```
# look in current directory for npm-shrinkwrap.json and install node modules
frosty install
```

## Options
```
  --cwd [DIR]          Look for npm-shrinkwrap.json in this directory.
  --cache-dir [DIR]    Use this directory to cache npm modules.
  --force              Continue installation even if one or more modules fail to install.
  --http-proxy [URL]   Use a proxy to reach the npm registry.
  --offline            Do not download modules which are not found in the local cache.
  --registry [URL]     Use an alternative npm registry (default is https://registry.npmjs.org)
  --verbose            Show verbose output.
```
