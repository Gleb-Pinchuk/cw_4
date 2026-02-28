from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habits.views import HabitViewSet, LoginView, RegisterView

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
