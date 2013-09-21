"""
default BFW configuration
"""

config = {
    'instance_pkgstores': ['tiddlywebplugins.bfw'],
    'static_url_dir': 'static',
    'static_file_dir': ('tiddlywebplugins.bfw', 'assets'),
    'wikitext.type_render_map': {
        'text/x-markdown': 'tiddlywebplugins.markdown'
    }
}
