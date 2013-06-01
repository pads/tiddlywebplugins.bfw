from httpexceptor import HTTP302, HTTP400, HTTP401, HTTP404, HTTP409, HTTP415

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User
from tiddlyweb.model.policy import Policy, UserRequiredError
from tiddlyweb.store import NoBagError, NoUserError
from tiddlyweb.web.util import get_route_value, make_cookie

from tiddlywebplugins.logout import logout as logout_handler
from tiddlywebplugins.templates import get_template


def frontpage(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')

    if current_user != 'GUEST': # auth'd
        raise HTTP302('%s/~' % server_prefix)
    else: # unauth'd
        uris = {
            'register': '%s/register' % server_prefix,
            'login': '%s/challenge' % server_prefix
        }
        return _render_template(environ, start_response, 'frontpage.html',
                uris=uris)


def user_home(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    if current_user == 'GUEST':
        raise HTTP401('unauthorized')

    return _render_template(environ, start_response, 'user_home.html',
            user=current_user)


def wiki_home(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    wiki_name = get_route_value(environ, 'wiki_name')

    store = environ['tiddlyweb.store']
    bag = _ensure_bag_exists(wiki_name, store)

    bag.policy.allows(environ['tiddlyweb.usersign'], 'read')

    return _render_template(environ, start_response, 'layout.html')


def create_wiki(environ, start_response):
    _ensure_form_submission(environ)

    current_user = environ['tiddlyweb.usersign']['name']
    if current_user == 'GUEST':
        raise HTTP401('unauthorized')

    wiki_name = environ['tiddlyweb.query']['wiki'][0] # TODO: validate
    private = environ['tiddlyweb.query'].get('private', [''])[0] == '1'
    store = environ['tiddlyweb.store']

    # check reserved terms
    blacklist = ['bags', 'recipes', 'wikis', 'pages', '~', 'register', 'logout'] # XXX: too manual, hard to keep in sync
    if wiki_name in blacklist:
        raise HTTP409('wiki name unavailable')

    bag = Bag(wiki_name)
    try:
        store.get(bag)
        raise HTTP409('wiki name unavailable')
    except NoBagError:
        pass

    read_constraint = [current_user] if private else None
    bag.policy = Policy(read=read_constraint , write=[current_user],
            create=[current_user], delete=[current_user], manage=[current_user]) # XXX: too limiting!?

    store.put(bag)

    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')
    wiki_uri = '%s/%s' % (server_prefix, wiki_name) # XXX: should include host!?

    start_response('303 See Other', [('Location', wiki_uri)])
    return ['']


def create_page(environ, start_response):
    _ensure_form_submission(environ)

    wiki_name = environ['tiddlyweb.query']['wiki'][0]
    title = environ['tiddlyweb.query']['title'][0] # TODO: validate
    text = environ['tiddlyweb.query']['text'][0]

    store = environ['tiddlyweb.store']
    bag = _ensure_bag_exists(wiki_name, store)

    bag.policy.allows(environ['tiddlyweb.usersign'], 'create')

    tiddler = Tiddler(title, bag.name)
    store.put(tiddler)

    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')
    page_uri = '%s/%s/%s' % (server_prefix, wiki_name, title) # XXX: should include host!?

    start_response('303 See Other', [('Location', page_uri)])
    return ['']


def register_user(environ, start_response):
    _ensure_form_submission(environ)

    username, password, confirmation = [environ['tiddlyweb.query'][param][0] for
            param in ('username', 'password', 'password_confirmation')]

    user = User(username)
    store = environ['tiddlyweb.store']
    try:
        store.get(user)
        raise HTTP409('username unavailable')
    except NoUserError:
        pass

    if not password == confirmation:
        raise HTTP400('passwords do not match')

    user.set_password(password)
    store.put(user)

    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')
    root_uri = '%s/' % server_prefix

    cookie = make_cookie('tiddlyweb_user', user.usersign, path=root_uri,
            mac_key=environ['tiddlyweb.config']['secret'],
            expires=environ['tiddlyweb.config'].get('cookie_age', None))

    start_response('303 See Other',
            [('Set-Cookie', cookie), ('Location', root_uri)])
    return ['']


def logout(environ, start_response):
    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')

    environ['tiddlyweb.query']['tiddlyweb_redirect'] = ['%s/' % server_prefix]
    return logout_handler(environ, start_response)


def _render_template(environ, start_response, name, status='200 OK', headers={},
        **data):
    template = get_template(environ, name)
    if not 'Content-Type' in headers: # XXX: case-sensitivity conflicts?
        headers['Content-Type'] = 'text/html; charset=UTF-8'
    start_response(status, headers.items())
    return template.generate(**data)


def _ensure_bag_exists(bag_name, store):
    bag = Bag(bag_name)
    try:
        bag = store.get(bag)
    except NoBagError:
        raise HTTP404('wiki not found')

    return bag


def _ensure_form_submission(environ): # TODO: turn into decorator
    content_type = environ.get('CONTENT_TYPE', '')
    if not content_type.startswith('application/x-www-form-urlencoded'):
        raise HTTP415('unsupported content type')
