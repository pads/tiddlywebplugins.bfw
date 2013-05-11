import httplib2
import wsgi_intercept

from wsgi_intercept import httplib2_intercept

from tiddlyweb.config import config
from tiddlyweb.web.serve import load_app


def setup_module(module):
    _initialize_app()


def test_response():
    http = httplib2.Http()
    response, content = http.request('http://example.org:8001/',
            method='GET', headers={ 'Accept': 'text/html' })
    assert response.status == 200
    assert response['content-type'] == 'text/html; charset=UTF-8'


def _initialize_app():
    config['server_host'] = {
        'scheme': 'http',
        'host': 'example.org',
        'port': '8001',
    }
    config['system_plugins'].append('tiddlywebplugins.bfw')

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('example.org', 8001, load_app)
