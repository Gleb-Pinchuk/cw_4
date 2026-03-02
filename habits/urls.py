from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import (
    HabitViewSet,
    PublicHabitViewSet,
    RegisterView,
    LoginView,
    CustomTokenRefreshView
)

# Основной роутер (личные привычки - требует авторизации)
router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

# Роутер для публичных привычек (без авторизации)
public_router = DefaultRouter()
public_router.register(r'', PublicHabitViewSet, basename='public-habits')

urlpatterns = [
    # Личные привычки
    path('habits/', include(router.urls)),

    # Публичные привычки (отдельный путь)
    path('habits/public/', include(public_router.urls)),

    # Авторизация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
