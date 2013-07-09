"""
basic structure and contents of a BFW
"""

store_contents = {}

store_structure = {
    'bags': {
        'assets': {
            'desc': 'Common assets',
            'policy': {
                'read': [],
                'write': ['R:ADMIN'],
                'create': ['R:ADMIN'],
                'delete': ['R:ADMIN'],
                'manage': ['R:ADMIN'],
                'owner': 'administrator',
            }
        }
    }
}

store_contents['assets'] = ['src/assets.recipe']

instance_config = {
    'system_plugins': ['tiddlywebplugins.bfw'],
    'twanager_plugins': ['tiddlywebplugins.bfw']
}
