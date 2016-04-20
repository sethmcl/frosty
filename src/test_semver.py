import unittest

from semver import parse_semver, sorted_semver, is_explicit


class TestSemver(unittest.TestCase):

    def test_parse_semver(self):
        expectations = [
            ['0.0.0-foobar', [0, 0, 0, 0]],
            ['0.0.0-foobar+meta', [0, 0, 0, 0]],
            ['1.0.0-foobar+meta', [1, 0, 0, 0]],
            ['1.1.1-foobar+meta', [1, 1, 1, 0]],
            ['1.1.1', [1, 1, 1, 1]],
            ['10.1.1', [10, 1, 1, 1]],
            ['10.1.100', [10, 1, 100, 1]],
            ['1.1.1+meta', [1, 1, 1, 1]],
            ['1a.b1c.1+meta', [1, 1, 1, 1]],
            ['50.5', [50, 5, 0, 1]],
        ]

        for pair in expectations:
            input = pair[0]
            actual = parse_semver(input)
            expected = pair[1]

            for (index, key) in enumerate(['major', 'minor', 'patch', 'label']):
                self.assertEqual(
                    actual[key],
                    expected[index],
                    'parsed %s value of %s was %s. expected %s' % (key, input, actual[key], expected[index])
                )


    def test_sorted_semver(self):
        expectations = [
            [['0.0.0'], ['0.0.0']],
            [['0.0.0', '0.0.1'], ['0.0.0', '0.0.1']],
            [['0.0.1', '0.0.0'], ['0.0.0', '0.0.1']],
            [['0.0.1', '0.10.0', '0.4.0'], ['0.0.1', '0.4.0', '0.10.0']],
            [['0.0.1', '0.10.0', '0.0.1-beta5', '0.4.0'], ['0.0.1-beta5', '0.0.1', '0.4.0', '0.10.0']],
            [['0.0.1', '0.10.0', '0.10.0+b', '0.0.1-beta5', '0.4.0'], ['0.0.1-beta5', '0.0.1', '0.4.0', '0.10.0', '0.10.0+b']],
        ]

        for pair in expectations:
            input = pair[0]
            actual = sorted_semver(input)
            expected = pair[1]
            self.assertEqual(
                actual,
                expected,
                'sorting input %s resulted in %s. expected %s.' % (input, actual, expected)
            )


    def test_is_explicit(self):
        expectations = [
            ['0.1.0', True],
            ['~0.1.0', False],
            ['^0.1.0', False],
            ['^~0.1.0', False],
            ['0.1.0-foo~', True],
            ['0.1.0-^foo', True],
            ['0.1.0-^foo', True],
            ['0.1.0-x6', True],
            ['0.9.x', False],
            ['0.9.X', False],
            ['0.9', False]
        ]

        for pair in expectations:
            input = pair[0]
            actual = is_explicit(input)
            expected = pair[1]
            self.assertEqual(
                actual,
                expected,
                'is_explicit(%s) returned %s. expected %s.' % (input, actual, expected)
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
