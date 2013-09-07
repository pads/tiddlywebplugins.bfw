"""
TiddlyWeb plugin initialization
"""

import sys
import shutil

from tiddlyweb.manage import make_command
from tiddlyweb.util import merge_config, std_error_message

from tiddlywebplugins.utils import replace_handler

from . import web, middleware
from .config import config as bfwconfig


def init(config):
    merge_config(config, bfwconfig)
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
    selector.add('/{wiki_name:segment}/{page_name:segment}', GET=web.wiki_page,
            PUT=web.wiki_page)


@make_command()
def assetcopy(args):
    """
    Copy BFW's static assets into specified target directory
    """
    from pkg_resources import resource_filename

    if len(args) != 1:
        std_error_message('ERROR: invalid target directory')
        sys.exit(1)

    target_dir = args[0]

    assets_path = resource_filename('tiddlywebplugins.bfw', 'assets')
    try:
        shutil.copytree(assets_path, target_dir)
    except OSError:
        std_error_message('ERROR: target directory already exists - aborted')
        sys.exit(2)


def _error_handler(status, message):
    return lambda environ, start_response: (middleware.
            render_error(environ, start_response, status, message=message))
