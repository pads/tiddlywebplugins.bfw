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
    from . import web, middleware

    config['server_response_filters'].insert(0, middleware.FriendlyError) # XXX: position arbitrary!?
    selector.status404 = _error_handler('404 Not Found', 'not found')
    selector.status405 = _error_handler('405 Method Not Allowed',
            'method not allowed')

    replace_handler(selector, '/', GET=web.frontpage)
    selector.add('/~', GET=web.home)
    selector.add('/register', POST=web.register_user)
    selector.add('/logout', POST=web.logout)


def _error_handler(status, message):
    return lambda environ, start_response: (middleware.
            render_error(environ, start_response, status, message=message))
    # XXX: accessing `middleware:render_error` is hacky, particularly because it
    #      relies on `middleware` having been imported by `init`
