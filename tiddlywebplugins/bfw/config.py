"""
default BFW configuration
"""

config = {
    'instance_pkgstores': ['tiddlywebplugins.bfw'],
    'bfw.extra_stores': {
        r'^assets$': ['tiddlywebplugins.pkgstore',
            { 'package': 'tiddlywebplugins.bfw', 'read_only': True }]
    }
}
