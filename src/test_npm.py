import os
import unittest

from npm import Npm


class TestNpm(unittest.TestCase):

    def test_get_module_paths(self):
        test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data', 'npm'))
        paths = Npm.get_module_paths(test_path)
        self.assertEqual(len(paths), 3)


    def test_stat_module(self):
        test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data', 'npm', 'node_modules', '1a'))
        actual = Npm.stat_module(test_path)
        expected = ('1a', '0.0.1')
        self.assertEqual(actual, expected)


    def test_build_dependency_tree(self):
        test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data', 'npm'))
        deps = Npm.build_dependency_tree(test_path)

        self.assertEqual(set(deps.keys()), set(['1a@0.0.1', '1b@1.0.0']))

        self.assertEqual(set(deps['1a@0.0.1'].keys()), set([]))
        self.assertEqual(set(deps['1b@1.0.0'].keys()), set(['1b-a@1.0.0']))
        self.assertEqual(set(deps['1b@1.0.0']['1b-a@1.0.0'].keys()), set([]))



if __name__ == '__main__':
    unittest.main(verbosity=2)
