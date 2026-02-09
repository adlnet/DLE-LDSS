from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomUserSerializer, LoginSerializer, RegisterSerializer


class RegisterView(generics.GenericAPIView):
    """User Registration API"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        POST request that takes in: email, password, first_name, and last_name
        """
        data = request.data
        username = data.get('username')
        password = data.get('password')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = authenticate(username=username, password=password)

        # logs the user in and assigns a sessionID
        login(request, user)

        # responds with a HTTP 201 created and the user details.
        user_data = CustomUserSerializer(user, context=self.get_serializer_context()).data
        result = {'user': user_data}
        return Response(result, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Logs user in and returns token"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        POST endpoint that accepts a username and password, returns the
        session id cookie on success
        """
        # read login info
        data = request.data
        username = data.get("username")
        password = data.get("password")

        # check that credentials aren't empty
        if username is None or password is None:
            result = {"info": "Username and Password is needed"}
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)

        # attempt login using credentials
        user = authenticate(username=username, password=password)

        # check if authentication was successful
        if user is None:
            result = {"info": "User does not exist"}
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)

        # complete login, creates session id cookie if none supplied
        login(request, user)

        # responds with user info and session id cookie
        user_data = CustomUserSerializer(user, context=self.get_serializer_context()).data
        result = {"user": user_data}
        return Response(result)


class IsLoggedInView(APIView):
    """Checks if a user is logged in"""
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Validates that a user has a valid sessionid
        """
        # if the user is not found/authenticated (invalid session id)
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        result = {"user": CustomUserSerializer(request.user).data}
        return Response(result, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logs current user out"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logs a user out of their session
        """
        logout(request)
        response = Response(status=status.HTTP_200_OK)
        return response
