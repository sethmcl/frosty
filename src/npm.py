import json
import os
import shutil
import subprocess
import time

from log import Log
from util import tree


class Npm(object):
    """Interface to invoking npm commands

    Args:
        config ([Config]): Runtime configuration

    """

    def __init__(self, config):
        self.config = config


    def is_module_osx_only(self, module_name, module_version):
        cmd = self.build_npm_cmd()
        module = '%s@%s' % (module_name, module_version)
        cmd.extend(['info', module, 'os'])
        module_os = subprocess.check_output(cmd)
        return module_os.strip() == 'darwin'


    def is_git_module(self, module_url):
        return 'github.com' in module_url


    def get_platform(self):
        """Return platform name (`uname -s`)"""
        return subprocess.check_output(['uname', '-s']).strip()


    def is_osx(self):
        return self.get_platform() == 'Darwin'


    def install(self, module_name, module_version, module_url, prefix_dir=None):
        if not self.is_osx() and not self.is_git_module(module_url) and self.is_module_osx_only(module_name, module_version):
            raise RuntimeError('Cannot install %s on platform %s' % (module_url, self.get_platform()))

        cmd = self.build_npm_cmd(prefix_dir=prefix_dir)
        cmd.extend(['install', module_url])

        attempts = 0
        attempt_delay = 5
        max_attempts = 10
        try_again = True

        while try_again:
            attempts = attempts + 1
            Log.info('Attempting to install node module %s (attempt #%s)', module_name, attempts)
            result, error = self.try_install(cmd)

            if result is True and error is None:
                try_again = False
            elif attempts < max_attempts:
                time.sleep(attempt_delay)
            else:
                raise error

        return os.path.join(prefix_dir, 'node_modules', module_name)


    def try_install(self, cmd):
        try:
            subprocess.check_output(cmd)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, e


    def build_npm_cmd(self, prefix_dir=None):
        """Generate npm command with correct flags, based on configuration

        Args:
            prefix_dir (str): Value passed to `npm install --prefix`.

        Returns:
            list: Npm command with flags

        """
        npm_cmd = ['npm']

        if prefix_dir:
            npm_cmd.extend(['--prefix', prefix_dir])

        if self.config.http_proxy:
            npm_cmd.extend(['--proxy', self.config.http_proxy])
            npm_cmd.extend(['--https-proxy', self.config.http_proxy])

        if self.config.verbose:
            npm_cmd.append('--verbose')

        if self.config.registry:
            npm_cmd.extend(['--registry', self.config.registry])

        return npm_cmd


    @staticmethod
    def get_module_paths(module_path):
        """
        given the path of a node module, calculate list of all dependent modules
        by recursively searching node_modules child directories
        """
        module_paths = []
        for root, _, _ in os.walk(module_path):
            try:
                Npm.stat_module(root)
                module_paths.append(root)
            except IOError:
                Log.verbose('%s is not a valid Node module. Skipping' % root)

        return module_paths


    @staticmethod
    def stat_module(path):
        """
        check if given path is a node module, defined by the presence of a
        valid package.json file
        """
        package_file = os.path.join(path, 'package.json')

        if not os.path.exists(package_file):
            raise IOError('File %s not found' % package_file)

        try:
            with open(package_file) as json_data:
                data = json.load(json_data)
                version = data['version']
                name = data['name']
                gitHead = data.get('gitHead', None)
                _resolved = data.get('_resolved', '')

                if _resolved[0:4] == 'git+' and gitHead:
                    version = gitHead

                return (name, version)
        except:
            raise IOError('Invalid file %s' % package_file)


    @staticmethod
    def build_dependency_tree(module_path):
        """
        given the path of a node module, calculate a dependency tree.
        each node in the tree represents a dependency, and contains
        name and version of the dependency.

        this should be run on a "fully materialized" module path, that is
        a path containing an npm module which has been "installed" and contains its
        dependencies on disk in descendent node_modules dirs
        """
        dep_map = {}
        dep_map[module_path] = tree()

        def get_deps_tree(check_path):
            if check_path == '/':
                raise RuntimeError('Unable to locate dep tree')
            if dep_map.get(check_path, None) != None:
                return dep_map[check_path]
            return get_deps_tree(os.path.dirname(check_path))

        for root, _, _ in os.walk(module_path):
            deps = get_deps_tree(root)

            try:
                stat = Npm.stat_module(root)
                new_deps = deps['%s@%s' % stat]
                dep_map[root] = new_deps
            except IOError:
                Log.verbose('%s is not a valid Node module. Skipping' % root)

        return dep_map[module_path]
