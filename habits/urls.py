from django.urls import path, include
from rest_framework.routers import DefaultRouter

from habits.views import (
    HabitViewSet,
    PublicHabitViewSet,
    RegisterView,
)

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

public_router = DefaultRouter()
public_router.register(r'', PublicHabitViewSet, basename='public-habits')

urlpatterns = [
    path('habits/', include(router.urls)),
    path('habits/public/', include(public_router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
