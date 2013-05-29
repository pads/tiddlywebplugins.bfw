import os
import shutil
import tempfile

import httplib2
import wsgi_intercept

from urllib import urlencode
from wsgi_intercept import httplib2_intercept
from pytest import raises

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User
from tiddlyweb.store import NoBagError
from tiddlyweb.config import config as CONFIG
from tiddlyweb.web.serve import load_app
from tiddlywebplugins.utils import get_store


ADMIN_COOKIE = 'tiddlyweb_user="admin:80b3ae26238e34742fc38f6554e1f710edae71f3"'


def setup_module(module):
    module.TMPDIR = tempfile.mkdtemp()

    _initialize_app(TMPDIR)

    module.STORE = get_store(CONFIG)
    user = User('admin')
    user.set_password('secret')
    STORE.put(user)


def teardown_module(module):
    shutil.rmtree(TMPDIR)


def test_root():
    response, content = _req('GET', '/')
    assert response.status == 200
    assert response['content-type'] == 'text/html; charset=UTF-8'

    assert '<a href="/challenge">Log in</a>' in content
    assert 'Register' in content

    response, content = _req('GET', '/', headers={ 'Cookie': ADMIN_COOKIE })

    assert response.status == 302
    assert response['location'] == '/~'


def test_home():
    response, content = _req('GET', '/~')
    assert response.status == 401

    response, content = _req('GET', '/~', headers={ 'Cookie': ADMIN_COOKIE })
    assert response.status == 200


def test_user_registration():
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'username': 'fnd',
        'password': 'foo',
        'password_confirmation': 'foo'
    }
    response, content = _req('POST', '/register', urlencode(data),
            headers=headers)

    assert response.status == 303
    assert 'tiddlyweb_user="fnd:' in response['set-cookie']


def test_login():
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'user': 'fnd',
        'password': 'foo'
    }
    response, content = _req('POST', '/challenge/cookie_form', urlencode(data),
            headers=headers)

    assert response.status == 303
    assert 'tiddlyweb_user="fnd:' in response['set-cookie']

    response, content = _req('POST', '/logout')

    assert response.status == 303
    assert response['set-cookie'] == 'tiddlyweb_user=; Max-Age=0; Path=/'
    assert response['location'] == 'http://example.org:8001/'


def test_wiki_creation():
    assert not _bag_exists('foo')

    default_headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'wiki': 'foo',
        'private': '1'
    }

    response, content = _req('POST', '/wikis')
    assert response.status == 415

    response, content = _req('POST', '/wikis', urlencode(data),
            headers=default_headers)
    assert response.status == 401
    assert not _bag_exists('foo')

    headers = { 'Cookie': ADMIN_COOKIE }
    headers.update(default_headers)
    response, content = _req('POST', '/wikis', urlencode(data), headers=headers)
    assert response.status == 303
    assert response['location'] == '/foo'
    assert _bag_exists('foo')

    response, content = _req('GET', '/foo', headers={ 'Cookie': ADMIN_COOKIE })
    assert response.status == 200

    response, content = _req('GET', '/bar')
    assert response.status == 404

    response, content = _req('GET', '/foo')
    assert response.status == 302
    assert response['location'].endswith('/challenge?tiddlyweb_redirect=%2Ffoo')

    headers = { 'Cookie': ADMIN_COOKIE }
    headers.update(default_headers)
    response, content = _req('POST', '/wikis', urlencode(data), headers=headers)
    assert response.status == 409

    data['wiki'] = 'wikis'
    response, content = _req('POST', '/wikis', urlencode(data), headers=headers)
    assert response.status == 409

    # TODO:
    # * test non-private wiki results
    # * test special characters in names


def test_errors():
    response, content = _req('GET', '/N/A')
    assert response.status == 404
    assert '<html>' in content
    assert 'not found' in content

    response, content = _req('POST', '/')
    assert response.status == 405
    assert '<html>' in content
    assert 'not allowed' in content

    response, content = _req('GET', '/~')
    assert response.status == 401
    assert '<html>' in content
    assert 'unauthorized' in content

    response, content = _req('POST', '/register')
    assert response.status == 415
    assert '<html>' in content
    assert 'unsupported' in content

    data = {
        'username': 'foo',
        'password': 'bar',
        'password_confirmation': 'baz'
    }
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    response, content = _req('POST', '/register', urlencode(data),
            headers=headers)
    assert response.status == 400
    assert '<html>' in content
    assert 'passwords do not match' in content

    data = {
        'username': 'admin',
        'password': 'foo',
        'password_confirmation': 'foo'
    }
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    response, content = _req('POST', '/register', urlencode(data),
            headers=headers)
    assert response.status == 409
    assert '<html>' in content
    assert 'username unavailable' in content


def _initialize_app(tmpdir): # XXX: side-effecty
    CONFIG['server_host'] = {
        'scheme': 'http',
        'host': 'example.org',
        'port': '8001',
    }
    # TODO: test with server_prefix
    CONFIG['system_plugins'].append('tiddlywebplugins.bfw')
    CONFIG['server_store'] = ['text', {
        'store_root': os.path.join(tmpdir, 'store')
    }]
    CONFIG['secret'] = '0d67d5bbb6c002614efeaf296330fb43'

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('example.org', 8001, load_app)


def _req(method, uri, body=None, **kwargs):
    http = httplib2.Http()
    http.follow_redirects = False
    return http.request('http://example.org:8001%s' % uri, method=method,
            body=body, **kwargs)


def _bag_exists(bag_name):
    bag = Bag(bag_name)
    try:
        STORE.get(bag)
        return True
    except NoBagError:
        return False
