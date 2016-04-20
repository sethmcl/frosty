__doc__ = '''python frosty.py [ARGS]

OVERVIEW

    This tool is used to install Npm modules, as specified in a npm-shrinkwrap.json
    file. Each module which is installed will be cached, in $HOME/.frosty by default.

    Benefits of this tool over vanilla npm:

    1. Modules are cached in a fully expanded, post-install state.
    2. This tool can be run in a fully offline mode, so that no network requests will take place.

DEPENDENCIES

    For correct operation, this script assumes that npm is installed
    and can be found in the system $PATH

'''

import os
import shutil
import subprocess
import sys
import traceback

from cache import Cache
from config import Config
from errors import MissingNpmShrinkwrap
from log import Log
from manifest import Manifest
from npm import Npm


class Frosty(object):

    def __init__(self):
        self.config = Config()

        if self.config.verbose:
            Log.show_verbose = True

        if self.config.offline:
            Log.verbose('[OFFLINE MODE]')

        self.npm = Npm(self.config)
        self.cache = Cache(self.config, self.npm)


    def run(self):
        try:
            manifest = Manifest(Manifest.locate_file(self.config.cwd))
            self.install(manifest)
        except MissingNpmShrinkwrap as e:
            Log.error(e.message)
            sys.exit(1)


    def install(self, manifest):
        if os.path.isdir(manifest.node_modules_path):
            shutil.rmtree(manifest.node_modules_path)
        os.mkdir(manifest.node_modules_path)
        self.install_deps_tree(manifest.deps, manifest.root_path)


    def install_deps_tree(self, deps, path):
        for key in deps.keys():
            (module, version, url) = key.split('===')

            try:
                self.install_module(module, version, url, path)
            except BaseException as e:
                Log.error('Failed to install %s@%s from %s', module, version, url)
                Log.info('self.config.force = %s', self.config.force)
                if self.config.force is False:
                    raise e

            self.install_deps_tree(deps[key], os.path.join(path, 'node_modules', module))


    def install_module(self, module, version, url, path):
        cache = self.cache
        config = self.config
        cache_hit = cache.query(module, version)

        if not cache_hit:
            if config.offline:
                sys.exit(1)
            else:
                cache.add(module, version, url)

        cache.materialize_module(module, version, path)

    @staticmethod
    def print_version():
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'version'))
        with open(path) as f:
            print(f.read().strip())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '-V', '--version']:
        Frosty.print_version()
    else:
        Frosty().run()

    sys.exit(0)
