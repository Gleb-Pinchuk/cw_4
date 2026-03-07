from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомного пользователя (с email вместо username)"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомный пользователь с email вместо username"""

    username = None
    email = models.EmailField('email address', unique=True)
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram ID')
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram username')

    USERNAME_FIELD = 'email'  # Поле для авторизации
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
