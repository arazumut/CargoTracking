from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import UserProfile

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile = getattr(user, 'profile', None)
            return Response({
                'message': 'Giriş başarılı',
                'username': user.username,
                'role': profile.role if profile else None
            })
        return Response({'error': 'Geçersiz kullanıcı adı veya şifre'}, status=status.HTTP_401_UNAUTHORIZED)

class RoleRequiredMixin:
    required_roles = []
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)
        return profile and profile.role in self.required_roles
