from django.http import JsonResponse
from rest_framework import status

class TokenExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            if ('<Response status_code=401, "application/json">' in str(response)) and ("code='token_not_valid'" in str(response.data)):raise
            return response
        except Exception as e:
            return JsonResponse({"message": "Session expired or Token invalid. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)