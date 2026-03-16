from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.serializers import CustomTokenObtainPairSerializer

urlpatterns = [
    path(
        'token/',
        TokenObtainPairView.as_view(
            serializer_class=CustomTokenObtainPairSerializer
        ),
        name='token_obtain_pair',
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),
]
