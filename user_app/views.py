from rest_framework import status
from rest_framework import generics, views
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate
from user_app.tasks import send_welcome_mail
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer

class RegisterUser(views.APIView):
    """
    This view allows users to register within the password manager application. 
    Upon receiving a POST request with user registration data, it validates the data, creates a new user account.
    Once registration is successful, the user receives a welcome email and a JSON response confirming the successful registration.
    If registration fails due to invalid data, the view returns an HTTP 400 response with error details.

    Raises: HTTP 400 Bad Request: If the provided registration data is invalid and HTTP 500 Internal Server Error: If there is an unexpected error during registration.
    Permission Classes: AllowAny: Anyone can register without any restrictions.
    Parameter: request (Request): HTTP request object containing registration data.
    Return: JSON response indicating registration success or failure.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.validated_data['username']
            mail = serializer.validated_data['email']
            send_welcome_mail.delay(user,mail)
            return Response({"message": "User registration successful. Please log in with your credentials."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginUser(views.APIView):
    """
    This view processes POST requests containing user credentials (username and password).
    If valid credentials are provided, it authenticates the user and generates an access token.
    The access token is returned in the response, granting the user access to protected endpoints.
    If authentication fails, an error response is returned with a message indicating invalid credentials.

    Permission Classes: AllowAny: Anyone can attempt to log in without restrictions.
    Parameter: request (Request): HTTP request object containing user login credentials.
    Return: JSON response containing the access token if authentication is successful.
    Otherwise, returns an error message indicating invalid credentials.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not (username or password):
            return Response({"message": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)

