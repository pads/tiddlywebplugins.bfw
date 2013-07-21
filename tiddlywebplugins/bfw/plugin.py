"""
TiddlyWeb plugin initialization
"""

from tiddlyweb.util import merge_config

from tiddlywebplugins.utils import replace_handler

from . import web, middleware
from .config import config as bfwconfig


def init(config):
    merge_config(config, bfwconfig)
    wrap_store(config)
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
    selector.add('/pages', POST=web.put_page) # XXX: bad URI?
    selector.add('/editor', GET=web.editor) # XXX: bad URI?
    selector.add('/logout', POST=web.logout)
    selector.add('/{wiki_name:segment}', GET=web.wiki_home)
    selector.add('/{wiki_name:segment}/{page_name:segment}', GET=web.wiki_page)

    config['wikitext.type_render_map']['text/x-markdown'] = 'tiddlywebplugins.markdown'


def wrap_store(config):
    """
    wrap a diststore around the configured store for packaged contents (read
    from `bfw.extra_stores`)
    """
    if config['server_store'][1].get('wrapped', None): # avoids infinite recurion -- XXX: shouldn't be necessary!?
        return

    original_store = config['server_store']
    config['server_store'] = ['tiddlywebplugins.diststore', {
        'main': original_store,
        'extras': config['bfw.extra_stores'].items(),
        'wrapped': True
    }]


def _error_handler(status, message):
    return lambda environ, start_response: (middleware.
            render_error(environ, start_response, status, message=message))
