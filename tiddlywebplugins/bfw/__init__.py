"""
wiki-like system for individuals and small teams, emphasizing micro-content and
based on TiddlyWeb (http://tiddlyweb.com)

https://github.com/FND/tiddlywebplugins.bfw
"""

__version__ = '0.0.1'
__author__ = 'FND'
__license__ = 'MIT'


def init(config):
    from . import plugin

    plugin.init(config)
