from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from habits.models import Habit
from habits.serializers import HabitSerializer, UserSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """Набор представлений для CRUD операций с привычками"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает привычки текущего пользователя + публичные привычки
        """
        user = self.request.user
        queryset = Habit.objects.filter(Q(user=user) | Q(is_public=True))
        return queryset

    def perform_create(self, serializer):
        """При создании сохраняем текущего пользователя как владельца"""
        serializer.save(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем токены для пользователя сразу после регистрации
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.CreateAPIView):
    """Авторизация пользователя (получение токена)"""

    serializer_class = UserSerializer  # <-- Добавлено для устранения ошибки
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }
            )
        return Response(
            {"error": "Неверные учетные данные"}, status=status.HTTP_400_BAD_REQUEST
        )
