import json
import os
import subprocess
import shutil

from log import Log
from npm import Npm


class Cache(object):
    """Represents the local bnpm managed cache

    Args:
        config ([Config]): Runtime configuration

    Attributes:
        cache_dir ([str]): Absolute path to root of cache on disk.

    Raises:

    """

    def __init__(self, config, npm):
        self.npm = npm
        self.config = config
        self.cache_dir = config.cache_dir
        self.temp_dir = os.path.join(self.cache_dir, '.temp')
        Log.verbose('Using cache directory %s', self.cache_dir)


    def query(self, module_name, module_version):
        cache_dir = self.get_module_path(module_name, module_version)
        Log.verbose('cache query for %s@%s (%s)', module_name, module_version, cache_dir)

        if os.path.isdir(cache_dir):
            Log.verbose('cache HIT for %s@%s (%s)', module_name, module_version, cache_dir)
            return True
        else:
            Log.verbose('cache MISS for %s@%s (%s)', module_name, module_version, cache_dir)
            return False


    def add(self, module_name, module_version, module_url):
        # remove temporary node_modules directory between npm installs to avoid peer dependency issues
        temp_node_modules = os.path.join(self.temp_dir, 'node_modules')
        if os.path.isdir(temp_node_modules):
            shutil.rmtree(temp_node_modules)

        temp_module_dir = None

        try:
            temp_module_dir = self.npm.install(module_name,
                                               module_version,
                                               module_url,
                                               prefix_dir=self.temp_dir)
        except RuntimeError as e:
            Log.error(e.message)
            raise e

        module_paths = [temp_module_dir] + Npm.get_module_paths(temp_module_dir)

        for module in module_paths:
            self.copy_module_to_cache(module)


    def copy_module_to_cache(self, temp_module_dir):
        # given a path, read the package.json to determine module name and version
        # copy to correct location in cache directory
        # remove child node_modules dir
        stat = Npm.stat_module(temp_module_dir)

        if not stat:
            return

        module_name = stat[0]
        module_version = stat[1]

        if self.query(module_name, module_version):
            return

        cache_module_dir = self.get_module_data_path(module_name, module_version)
        Log.verbose('copy %s@%s to cache...', module_name, module_version)
        shutil.copytree(temp_module_dir, cache_module_dir)

        # create frozen list of module deps
        self.write_module_deps_to_json(module_name, module_version)

        child_node_modules = os.path.join(cache_module_dir, 'node_modules')
        if os.path.isdir(child_node_modules):
            shutil.rmtree(child_node_modules)


    def write_module_deps_to_json(self, module_name, module_version):
        deps = Npm.build_dependency_tree(self.get_module_data_path(module_name, module_version))
        json_str = json.dumps(deps, sort_keys=True, indent=4, separators=(',', ': '))
        deps_file = self.get_module_deps_path(module_name, module_version)
        with open(deps_file, 'w') as file:
            file.write(json_str)


    def get_module_path(self, module_name, module_version):
        return os.path.join(self.cache_dir, module_name, module_version)


    def get_module_deps_path(self, module_name, module_version):
        return os.path.join(self.get_module_path(module_name, module_version), 'deps.json')


    def get_module_data_path(self, module_name, module_version):
        return os.path.join(self.get_module_path(module_name, module_version), 'data')


    def load_module_deps_from_json(self, module_name, module_version):
        deps_file = self.get_module_deps_path(module_name, module_version)
        with open(deps_file) as file:
            return json.load(file)


    def materialize_module(self, module_name, module_version, project_dir):
        cache_module_dir = self.get_module_data_path(module_name, module_version)
        project_module_dir = os.path.join(project_dir, 'node_modules', module_name)

        if os.path.isdir(project_module_dir):
            shutil.rmtree(project_module_dir)
        shutil.copytree(cache_module_dir, project_module_dir)

        # set up symlink for .bin target
        bin = {}
        nm_dir = os.path.dirname(project_module_dir)
        bin_dir = os.path.join(nm_dir, '.bin')
        with open(os.path.join(project_module_dir, 'package.json')) as file:
            bin = json.load(file).get('bin', {})
        for (name, path) in bin.items():
            bin_path = os.path.relpath(os.path.realpath(os.path.join(project_module_dir, path)), bin_dir)
            bin_ln = os.path.join(bin_dir, name)
            if not os.path.isdir(bin_dir):
                os.makedirs(bin_dir)
            subprocess.check_output(['ln', '-sf', bin_path, bin_ln])
