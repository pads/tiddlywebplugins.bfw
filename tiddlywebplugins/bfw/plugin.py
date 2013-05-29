"""
TiddlyWeb plugin initialization
"""

from tiddlywebplugins.utils import replace_handler
from . import web, middleware


def init(config):
    try:
        selector = config['selector']
    except KeyError: # twanager mode
        return

    config['server_response_filters'].insert(0, middleware.FriendlyError) # XXX: position arbitrary!?
    selector.status404 = _error_handler('404 Not Found', 'not found')
    selector.status405 = _error_handler('405 Method Not Allowed',
            'method not allowed')

    replace_handler(selector, '/', GET=web.frontpage)
    selector.add('/~', GET=web.user_home)
    selector.add('/register', POST=web.register_user) # XXX: verb as URI
    selector.add('/wikis', POST=web.create_wiki) # XXX: bad URI?
    selector.add('/logout', POST=web.logout)
    selector.add('/{wiki_name:segment}', GET=web.wiki_home)


def _error_handler(status, message):
    return lambda environ, start_response: (middleware.
            render_error(environ, start_response, status, message=message))
