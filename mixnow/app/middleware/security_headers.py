# core/middleware/security_headers.py

class RemoveServerHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Elimina la cabecera "Server"
        if 'Server' in response:
            del response['Server']
        return response
