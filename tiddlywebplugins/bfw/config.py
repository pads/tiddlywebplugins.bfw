"""
default BFW configuration
"""

config = {
    'static_url_dir': 'static',
    'static_file_dir': ('tiddlywebplugins.bfw', 'assets'),
    'wikitext.type_render_map': {
        'text/x-markdown': 'tiddlywebplugins.markdown'
    }
}
