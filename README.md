Frosty (Node.js)
================

This tool is used to install Npm modules, as specified in a npm-shrinkwrap.json
file. Each module which is installed will be cached, in $HOME/.frosty by default.

Benefits of this tool over vanilla npm:

1. Modules are cached in a fully expanded, post-install state.
2. This tool can be run in a fully offline mode, so that no network requests will take place.

## Usage
```
# pull from internet if module is not cached
bin/frosty install

# only use local cache. fail if any cache query misses
bin/frosty install --offline
```
