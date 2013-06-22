from urllib import quote

from httpexceptor import HTTP302, HTTP400, HTTP401, HTTP404, HTTP409, HTTP415

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User
from tiddlyweb.model.policy import Policy, UserRequiredError, ForbiddenError
from tiddlyweb.store import NoBagError, NoUserError
from tiddlyweb.web.util import get_route_value, make_cookie

from tiddlywebplugins.logout import logout as logout_handler
from tiddlywebplugins.templates import get_template


def ensure_form_submission(fn): # TODO: move elsewhere
    """
    decorator to ensure the request was a form submission
    """

    def wrapper(environ, start_response):
        content_type = environ.get('CONTENT_TYPE', '')
        if not content_type.startswith('application/x-www-form-urlencoded'):
            raise HTTP415('unsupported content type')

        return fn(environ, start_response)

    return wrapper


def frontpage(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']

    if current_user != 'GUEST': # auth'd
        raise HTTP302(_uri(environ, '~'))
    else: # unauth'd
        uris = {
            'register': _uri(environ, 'register'),
            'login': _uri(environ, 'challenge', tiddlyweb_redirect='/~')
        }
        return _render_template(environ, start_response, 'frontpage.html',
                uris=uris)


def user_home(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    if current_user == 'GUEST':
        raise HTTP401('unauthorized')

    store = environ['tiddlyweb.store']
    wikis = []
    for bag in store.list_bags():
        try:
            bag = store.get(bag) # XXX: this should not be necessary!?
            bag.policy.allows(environ['tiddlyweb.usersign'], 'read')
            uri = _uri(environ, bag.name)
            wikis.append({ 'name': bag.name, 'uri': uri })
        except ForbiddenError, exc:
            pass

    uris = {
        'create_wiki': _uri(environ, 'wikis'),
        'create_page': _uri(environ, 'pages')
    }
    return _render_template(environ, start_response, 'user_home.html',
            user=current_user, wikis=wikis, uris=uris)


def wiki_home(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    wiki_name = get_route_value(environ, 'wiki_name')

    store = environ['tiddlyweb.store']
    bag = _ensure_bag_exists(wiki_name, store)

    bag.policy.allows(environ['tiddlyweb.usersign'], 'read')

    return _render_template(environ, start_response, 'layout.html')


@ensure_form_submission
def create_wiki(environ, start_response):
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
    bag.policy = Policy(read=read_constraint, write=[current_user],
            create=[current_user], delete=[current_user], manage=[current_user]) # XXX: too limiting!?

    store.put(bag)

    wiki_uri = _uri(environ, wiki_name).encode('UTF-8') # XXX: should include host!?
    start_response('303 See Other', [('Location', wiki_uri)])
    return ['']


@ensure_form_submission
def create_page(environ, start_response):
    wiki_name = environ['tiddlyweb.query']['wiki'][0]
    title = environ['tiddlyweb.query']['title'][0] # TODO: validate
    text = environ['tiddlyweb.query']['text'][0]

    store = environ['tiddlyweb.store']
    bag = _ensure_bag_exists(wiki_name, store)

    bag.policy.allows(environ['tiddlyweb.usersign'], 'create')

    tiddler = Tiddler(title, bag.name)
    tiddler.text = text
    store.put(tiddler) # XXX: overwrites existing tiddlers

    page_uri = _uri(environ, wiki_name, title).encode('UTF-8') # XXX: should include host!?
    start_response('303 See Other', [('Location', page_uri)])
    return ['']


@ensure_form_submission
def register_user(environ, start_response):
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

    root_uri = _uri(environ, '')

    cookie = make_cookie('tiddlyweb_user', user.usersign, path=root_uri,
            mac_key=environ['tiddlyweb.config']['secret'],
            expires=environ['tiddlyweb.config'].get('cookie_age', None))

    start_response('303 See Other',
            [('Set-Cookie', cookie), ('Location', root_uri.encode('UTF-8'))])
    return ['']


def logout(environ, start_response):
    environ['tiddlyweb.query']['tiddlyweb_redirect'] = [_uri(environ, '')]
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


def _uri(environ, *segments, **query_params):
    server_prefix = environ['tiddlyweb.config'].get('server_prefix', '')
    uri = '/'.join([server_prefix] + [_encode(segment) for segment in segments])

    if query_params:
        uri += '?%s' % ';'.join('%s=%s' % (_encode(key), _encode(value))
                for key, value in query_params.items())

    return uri


def _encode(uri_component):
    return quote(uri_component, safe='')
