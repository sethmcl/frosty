import argparse
import os


class Config(object):
    """Represents the context for an invocation of the frosty command.
    """

    def __init__(self):
        self.__dict__ = self.parse_cli_args().__dict__


    def parse_cli_args(self):
        """Parse command line arguments and return object with values"""

        parser = argparse.ArgumentParser(usage=__doc__)

        parser.add_argument('install', help='perform install action')
        parser.add_argument('-C', '--cwd', required=False, type=str, help='run in this directory', default=os.getcwd())
        parser.add_argument('-d', '--cache-dir', required=False, type=str, help='Cache directory', default=os.path.expandvars('$HOME/.frosty'))
        parser.add_argument('-f', '--force', required=False, action='store_true', help='Force install to continue, even if an individual module fails to install')
        parser.add_argument('-o', '--offline', action='store_true', help='do not connect to remote npm registry')
        parser.add_argument('-p', '--http-proxy', help='url of proxy to use for reaching npm')
        parser.add_argument('-r', '--registry', default='https://registry.npmjs.org', help='url of npm registry')
        parser.add_argument('-v', '--verbose', action='store_true', help='print verbose output')

        return parser.parse_args()
