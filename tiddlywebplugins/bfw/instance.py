"""
basic structure and contents of a BFW
"""

store_structure = {
    'users': {
        'bfw': {} # not to be used as regular user
    },
    'bags': {
        'assets': {
            'desc': 'common assets',
            'policy': {
                'read': [],
                'write': ['R:ADMIN'],
                'create': ['R:ADMIN'],
                'delete': ['R:ADMIN'],
                'manage': ['R:ADMIN'],
                'owner': 'bfw',
            }
        }
    }
}

store_contents = {
    'assets': ['src/assets.recipe']
}

instance_config = {
    'system_plugins': ['tiddlywebplugins.bfw'],
    'twanager_plugins': ['tiddlywebplugins.bfw']
}
