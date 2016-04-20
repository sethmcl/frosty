import json
import os

from errors import MissingNpmShrinkwrap
from util import tree


class Manifest(object):
    """Represents node project manifest file

    Can be either npm-shrinkwrap.json or package.json

    Args:
        config ([Config]): Runtime configuration

    Attributes:

    Raises:

    """

    def __init__(self, manifest_path):
        self.json = Manifest.read(manifest_path)
        self.deps = Manifest.build_dependency_tree(self.json)
        self.root_path = os.path.dirname(manifest_path)
        self.node_modules_path = os.path.join(self.root_path, 'node_modules')


    def get_deps(self):
        full_dep_list = tree()
        deps = self.json.get('dependencies', None)

        if deps:
            for key in deps.keys():
                full_dep_list['%s@%s' % (key, deps[key])] = tree()

        return full_dep_list


    @staticmethod
    def build_dependency_tree(json):
        deps = tree()
        Manifest.append_dependencies_to_tree(deps, json.get('dependencies', {}))
        Manifest.append_dependencies_to_tree(deps, json.get('devDependencies', {}))
        return deps


    @staticmethod
    def append_dependencies_to_tree(deps, dep_json):
       for key in dep_json.keys():
           value = dep_json.get(key, None);

           sub_deps = tree()
           version = value.get('version', None)
           resolved_url = value.get('resolved', None)
           sub_dep_json = value.get('dependencies', {})

           if not resolved_url:
               resolved_url = Manifest.calculate_resolved_url(key, version)
           if type(version) not in [str, unicode]:
               raise RuntimeError('Invalid value %s for %s.version, expected str' % (version, key))
           if type(sub_dep_json) is not dict:
               raise RuntimeError('Invalid value %s for %s.dependencies, expected dict' % (sub_dep_json, key))

           if resolved_url[0:4] == 'git+':
               # Get commit sha from URL string
               version = resolved_url.split('#')[-1]

           deps['%s===%s===%s' % (key, version, resolved_url)] = sub_deps
           Manifest.append_dependencies_to_tree(sub_deps, sub_dep_json)


    @staticmethod
    def calculate_resolved_url(name, version):
        return 'https://registry.npmjs.org/%s/-/%s-%s.tgz' % (name, name, version)


    @staticmethod
    def read(manifest_path):
        '''Read manifest file. Expect file to be valid JSON.
        '''

        with open(manifest_path) as file:
            return json.load(file)


    @staticmethod
    def locate_file(cwd):
        if cwd is None:
            cwd = os.getcwd()

        if not os.path.isdir(cwd):
            raise RuntimeError('%s does not exist' % cwd)

        shrinkwrap_path = os.path.abspath(os.path.join(cwd, 'npm-shrinkwrap.json'))

        if os.path.isfile(shrinkwrap_path):
            return shrinkwrap_path

        # TODO: Handling package.json is not implemented yet
        # package_path = os.path.abspath(os.path.join(cwd, 'package.json'))
        # if os.path.isfile(package_path):
        #     return package_path

        raise MissingNpmShrinkwrap('Cannot find npm-shrinkwrap.json %s' % cwd)
