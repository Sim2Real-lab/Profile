class CleanHeadMiddleware:
    """
    Middleware that empties response content for HTTP HEAD requests.
    Prevents WSGI servers (like Gunicorn/WhiteNoise) from logging RFC 9110 warnings:
    'WSGI app sent body bytes on a no-body response (method=HEAD status=200); dropping per RFC 9110.'
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'HEAD':
            response.content = b''
        return response
