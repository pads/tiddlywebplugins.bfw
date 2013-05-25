from httpexceptor import HTTP302, HTTP400, HTTP401, HTTP409, HTTP415

from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError
from tiddlyweb.web.util import make_cookie

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


def home(environ, start_response):
    current_user = environ['tiddlyweb.usersign']['name']
    if current_user == 'GUEST':
        raise HTTP401

    return _render_template(environ, start_response, 'home.html',
            user=current_user)


def register_user(environ, start_response):
    _ensure_form_submission(environ)

    username, password, confirmation = [environ['tiddlyweb.query'][param][0] for
            param in ('username', 'password', 'password_confirmation')]

    user = User(username)
    store = environ['tiddlyweb.store']
    try:
        store.get(user)
        raise HTTP409('username unavailable') # TODO: friendly error page
    except NoUserError:
        pass

    if not password == confirmation:
        raise HTTP400('passwords do not match') # TODO: friendly error page

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


def _ensure_form_submission(environ): # TODO: turn into decorator
    content_type = environ.get('CONTENT_TYPE', '')
    if not content_type.startswith('application/x-www-form-urlencoded'):
        raise HTTP415 # TODO: friendly error page
