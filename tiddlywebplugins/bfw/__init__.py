"""
wiki-like system for individuals and small teams, emphasizing micro-content and
based on TiddlyWeb (http://tiddlyweb.com)

https://github.com/FND/tiddlywebplugins.bfw
"""

__version__ = '0.0.1'
__author__ = 'FND'
__license__ = 'MIT'


def init(config):
    try:
        selector = config['selector']
    except KeyError: # twanager mode
        return

    from tiddlywebplugins.utils import replace_handler
    from . import web

    replace_handler(selector, '/', GET=web.frontpage)
    selector.add('/~', GET=web.home)
    selector.add('/register', POST=web.register_user)
    selector.add('/logout', POST=web.logout)
