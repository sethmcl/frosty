import os
import unittest

from errors import MissingNpmShrinkwrap
from manifest import Manifest
from util import tree


class TestManifest(unittest.TestCase):

    def test_locate_package_json(self):
        cwd = relative_path('package_json')

        with self.assertRaises(MissingNpmShrinkwrap):
            actual = Manifest.locate_file(cwd)


    def test_locate_shrinkwrap_json(self):
        cwd = relative_path('shrinkwrap_json')
        actual = Manifest.locate_file(cwd)
        self.assertEqual('/test_data/manifest/shrinkwrap_json' in actual, True)


    def test_locate_bad_path(self):
        with self.assertRaises(RuntimeError) as context:
            Manifest.locate_file('/sanoteh/aeonstuh/234234')


    def test_locate_missing_manifest(self):
        cwd = relative_path('no_json')
        with self.assertRaises(MissingNpmShrinkwrap) as context:
            Manifest.locate_file(cwd)


    def test_read(self):
        data = Manifest.read(relative_path('simple', 'package.json'))
        self.assertEqual(data['name'], 'icy')
        self.assertEqual(len(data.keys()), 1)


    def test_append_dependencies_to_tree_dicts(self):
        dep_json = {
            'buffer': {
                'version': '4.0.0',
                'dependencies': {
                    'bar': {
                        'version': '0.0.1',
                        'dependencies': {
                            'biz': {
                                'version': '0.0.2'
                            },
                            'fiz': {
                                'version': '9.0.0',
                                'from': 'git+http://github.com/fiz',
                                'resolved': 'git+http://github.com/fiz#abc123'
                            }
                        },
                    }
                }
            },
            'io': {
                'version': '0.0.1'
            }
        }

        deps = tree()
        Manifest.append_dependencies_to_tree(deps, dep_json)
        expected = tree()

        buffer_str = 'buffer===4.0.0===https://registry.npmjs.org/buffer/-/buffer-4.0.0.tgz'
        bar_str = 'bar===0.0.1===https://registry.npmjs.org/bar/-/bar-0.0.1.tgz'
        biz_str = 'biz===0.0.2===https://registry.npmjs.org/biz/-/biz-0.0.2.tgz'
        io_str = 'io===0.0.1===https://registry.npmjs.org/io/-/io-0.0.1.tgz'
        fiz_str = 'fiz===abc123===git+http://github.com/fiz#abc123'

        expected[buffer_str][bar_str][biz_str] = tree()
        expected[buffer_str][bar_str][fiz_str] = tree()
        expected[io_str] = tree()
        self.assertEqual(deps, expected)


    def test_append_dependencies_to_tree_dicts_invalid_version_json(self):
        dep_json = {
            'buffer': {
                'version': False
            }
        }

        with self.assertRaises(RuntimeError) as context:
            Manifest.append_dependencies_to_tree(tree(), dep_json)


    def test_append_dependencies_to_tree_dicts_invalid_dep_json(self):
        dep_json = {
            'buffer': {
                'version': '0.0.1',
                'dependencies': False
            }
        }

        with self.assertRaises(RuntimeError) as context:
            Manifest.append_dependencies_to_tree(tree(), dep_json)


    def test_parse_npm_shrinkwrap_json(self):
        mani = Manifest(relative_path('shrinkwrap_json', 'npm-shrinkwrap.json'))
        expected = tree()

        buffer_str = u'buffer===4.4.0===https://registry.npmjs.org/buffer/-/buffer-4.4.0.tgz'
        base64_js_str = u'base64-js===1.0.2===https://registry.npmjs.org/base64-js/-/base64-js-1.0.2.tgz'
        ieee754_str = u'ieee754===1.1.6===https://registry.npmjs.org/ieee754/-/ieee754-1.1.6.tgz'
        isarray_str = u'isarray===1.0.0===https://registry.npmjs.org/isarray/-/isarray-1.0.0.tgz'

        expected[buffer_str][base64_js_str] = tree()
        expected[buffer_str][ieee754_str] = tree()
        expected[buffer_str][isarray_str] = tree()

        self.assertEqual(mani.deps, expected)


def relative_path(*nargs):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data', 'manifest', *nargs))


if __name__ == '__main__':
    unittest.main(verbosity=2)
