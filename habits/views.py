from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny

from habits.models import Habit, User
from habits.serializers import HabitSerializer, UserSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    Личные привычки пользователя (требует авторизации)
    """
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает ТОЛЬКО свои привычки"""
        user = self.request.user
        queryset = Habit.objects.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Публичные привычки (ДОСТУПНО ВСЕМ без авторизации)
    """
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  # <-- Разрешаем всем

    def get_queryset(self):
        """Возвращает только публичные привычки"""
        return Habit.objects.filter(is_public=True)


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    """Авторизация пользователя (получение токена)"""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """Обновление access токена"""
    permission_classes = [AllowAny]  # <-- Важно для refresh

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response
