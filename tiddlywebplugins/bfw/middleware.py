from httpexceptor import HTTPException

from .web import _render_template # XXX: smell


class FriendlyError(object):
    """
    WSGI middleware to trap HTTP4* exceptions, rendering them into HTML pages
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        try:
            return self.application(environ, start_response)
        except HTTPException, exc:
            if exc.status.startswith('4'):
                return render_error(environ, start_response, exc.status,
                        message=exc.message)
            else:
                raise


def render_error(environ, start_response, status, **kwargs):
    kwargs['status'] = status
    return _render_template(environ, start_response, 'error.html', **kwargs)
