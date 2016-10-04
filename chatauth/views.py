import redis

from django.contrib.auth import login
from django.core.exceptions import PermissionDenied

from rest_framework import generics, permissions, response, status

from .serializers import LoginSerializer, SignupSerializer


class SignupView(generics.CreateAPIView):
    permission_classes = permissions.AllowAny,
    serializer_class = SignupSerializer


class LoginView(generics.CreateAPIView):
    permission_classes = permissions.AllowAny,
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user is None:
            raise PermissionDenied

        login(request, user)
        token = request.session._session_key

        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        rstore = redis.Redis(connection_pool=pool)
        rstore.set('user:token:{}'.format(user.pk), token)

        return response.Response({
            'token': token,
        }, status=status.HTTP_200_OK)
