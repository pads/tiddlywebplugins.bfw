import os
import shutil
import tempfile

import httplib2
import wsgi_intercept

from urllib import urlencode
from wsgi_intercept import httplib2_intercept

from tiddlyweb.config import config as CONFIG
from tiddlyweb.web.serve import load_app


def setup_module(module):
    module.TMPDIR = tempfile.mkdtemp()
    _initialize_app(TMPDIR)


def teardown_module(module):
    shutil.rmtree(TMPDIR)


def test_root():
    response, content = _req('GET', '/')
    assert response.status == 200
    assert response['content-type'] == 'text/html; charset=UTF-8'

    assert '<a href="/challenge">Log in</a>' in content
    assert 'Register' in content


def test_user_registration():
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'username': 'fnd',
        'password': 'foo',
        'password_confirmation': 'foo'
    }
    response, content = _req('POST', '/register', urlencode(data),
            headers=headers)
    assert response.status == 302


def test_login():
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'user': 'fnd',
        'password': 'foo'
    }
    try:
        _req('POST', '/challenge/cookie_form', urlencode(data),
                headers=headers, redirections=0)
    except httplib2.RedirectLimit, exc:
        redirected = True
        response = exc.response
        content = exc.content

    assert redirected
    assert response.status == 303
    assert 'tiddlyweb_user="fnd:' in response['set-cookie']


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

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('example.org', 8001, load_app)


def _req(method, uri, body=None, **kwargs):
    http = httplib2.Http()
    return http.request('http://example.org:8001%s' % uri, method=method,
            body=body, **kwargs)
