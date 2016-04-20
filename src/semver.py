import re


def parse_semver(semver):
    """Parse a semantic version string to a dict.

    We define a semantic version string (http://semver.org/) s conforming to
    the format [MAJOR].[MINOR].[PATCH]-[LABEL]+[META].

    Args:
        semver (str): A semantic version string (ex: 1.10.0-pre)

    Returns:
        dict: A dictionary containing the parsed values

        The returned dictionary will contain:

            {
                'major': int,
                'minor': int,
                'patch': int,
                'label': int
            }

    The 'major', 'minor', and 'patch' items will be the int values of their corresponding sections from the input string.
    The 'label' item will be 1 if the input string did not contain a label, and 0 otherwise.

    Examples:

        invocation:
            semver('1.24.34-pre')

        return value:
            {
                'major': 1,
                'minor': 24,
                'patch': 34,
                'label': 0
            }

        invocation:
            semver('99.0.34+alt')

        return value:
            {
                'major': 99,
                'minor': 0,
                'patch': 34,
                'label': 1
            }
    """

    parts = [
        [], # MAJOR
        [], # MINOR
        [], # PATCH
        [], # LABEL
    ]

    parts_idx = 0
    part = parts[parts_idx]

    for index, character in enumerate(semver):
        is_last_character = index == (len(semver) - 1)

        if re.match('[0-9]', character):
            part.append(character)

        if character in ['.', '-', '+'] or is_last_character:
            parts_idx = parts_idx + 1
            part = parts[parts_idx]

        if character == '-':
            parts[parts_idx].append(True)
            break

        if character == '+':
            break

    parsed_semver = {
        'major': 0,
        'minor': 0,
        'patch': 0,
        'label': 1
    }

    if len(parts[0]) > 0:
        parsed_semver['major'] = int(''.join(parts[0]))

    if len(parts[1]) > 0:
        parsed_semver['minor'] = int(''.join(parts[1]))

    if len(parts[2]) > 0:
        parsed_semver['patch'] = int(''.join(parts[2]))

    if len(parts[3]) > 0:
        parsed_semver['label'] = 0

    return parsed_semver


def semver_cmp(a, b):
    """Compare two semantic version strings, used for sorting semver values

    Args:
        a (str): The first semantic version string
        b (str): The second semantic version string

    Returns:
        int: -1 if b is larger than a
             0 if b and a are equal
             1 if a is larger than b

    Comparison algorithm:

    1. First, compare the MAJOR version.
    2. If they are the same, compare the MINOR version.
    3. If they are the same, compare the PATCH version.
    4. If those are all the same, check if the version has a LABEL - ignore the content of the LABEL.
       A version with a LABEL (pre-release) comes before one without a LABEL (final release.)
    5. Ignore the content of META.

    The previous example list, in sorted order:

    - 0.0.0
    - 1.0.0-beta5+x95
    - 1.0.0+x95
    - 1.24.34-pre
    """

    a_parsed = parse_semver(a)
    b_parsed = parse_semver(b)

    if a_parsed['major'] != b_parsed['major']:
        return a_parsed['major'] - b_parsed['major']

    if a_parsed['minor'] != b_parsed['minor']:
        return a_parsed['minor'] - b_parsed['minor']

    if a_parsed['patch'] != b_parsed['patch']:
        return a_parsed['patch'] - b_parsed['patch']

    return a_parsed['label'] - b_parsed['label']


def sorted_semver(semvers):
  return sorted(semvers, cmp=semver_cmp)


def is_explicit(semver):
    """Determine if a semver string is explicit

    For example, `0.1.0` is explicit. `0.1.x` is not explicit.

    Args:
        semver (str): The semantic version string to evaluate

    Returns:
        bool: True if string is explicit. False otherwise.
    """
    major_minor_patch = semver.split('-')[0]

    if re.search('\^|~|x|X', major_minor_patch) or len(semver.split('.')) < 3:
        return False
    return True

