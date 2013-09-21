import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from tiddlywebplugins.bfw import (__version__ as VERSION, __author__ as AUTHOR,
        __license__ as LICENSE, __doc__ as DESC)


META = {
    'name': 'tiddlywebplugins.bfw',
    'url': 'https://github.com/FND/tiddlywebplugins.bfw',
    'version': VERSION,
    'description': 'Barely Functioning Wiki',
    'long_description': DESC.strip(),
    'license': LICENSE,
    'author': AUTHOR,
    'author_email': '',
    'maintainer': 'FND',
    'packages': find_packages(exclude=['test']),
    'scripts': ['bfwinstance'],
    'platforms': 'Posix; MacOS X; Windows',
    'include_package_data': True,
    'zip_safe': False,
    'install_requires': ['tiddlyweb', 'tiddlywebplugins.utils',
            'tiddlywebplugins.logout', 'tiddlywebplugins.static',
            'tiddlywebplugins.templates', 'tiddlywebplugins.markdown>=1.1.0',
            'markdown-checklist>=0.2.0', 'tiddlywebplugins.imaker'],
    'extras_require': {
        'build': ['tiddlywebplugins.ibuilder'],
        'testing': ['pytest', 'wsgi-intercept', 'httplib2'],
        'coverage': ['figleaf', 'coverage']
    }
}


# entry point for tests (required because `coverage` fails to invoke `py.test`
# in Travis CI's virtualenv)

class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

META['cmdclass'] = { 'test': PyTest }


if __name__ == '__main__':
    setup(**META)
