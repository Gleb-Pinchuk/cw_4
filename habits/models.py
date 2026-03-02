from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


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

    username = None  # Отключаем username
    email = models.EmailField('email address', unique=True)
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram ID')
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram username')

    USERNAME_FIELD = 'email'  # Поле для авторизации
    REQUIRED_FIELDS = []  # Какие поля требуются при создании суперпользователя

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')

    # Место — место, в котором необходимо выполнять привычку
    place = models.CharField(max_length=200, blank=True, null=True)

    # Время — время, когда необходимо выполнять привычку
    time = models.TimeField()

    # Действие — действие, которое представляет собой привычка
    action = models.CharField(max_length=200)

    # Признак приятной привычки
    is_pleasant = models.BooleanField(default=False)

    # Связанная привычка (например, приятная привычка в награду)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_by'
    )

    # Периодичность (в днях). По умолчанию 1 (ежедневно)
    frequency = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    # Вознаграждение (текстовое описание)
    reward = models.CharField(max_length=200, blank=True, null=True)

    # Время на выполнение (в минутах). Максимум 2 минуты
    duration = models.PositiveIntegerField(
        validators=[MaxValueValidator(2)],
        help_text="Время в минутах (максимум 2 минуты)"
    )

    # Признак публичности
    is_public = models.BooleanField(default=False)

    # Дата создания (автоматически)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Привычка: {self.action} ({self.user.email})"

    def clean(self):
        # Валидаторы для логики привычек
        if self.is_pleasant:
            if self.reward:
                raise ValidationError("У приятной привычки не может быть вознаграждения.")
            if self.related_habit:
                raise ValidationError("У приятной привычки не может быть связанной привычки.")

        if not self.is_pleasant:
            if self.reward and self.related_habit:
                raise ValidationError(
                    "Нельзя одновременно указать вознаграждение и связанную привычку. Выберите что-то одно."
                )

        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна иметь признак 'приятной'.")
