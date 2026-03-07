from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')

    # Место — место, в котором необходимо выполнять привычку
    place = models.CharField(max_length=200, blank=True, null=True)

    # Время — время, когда необходимо выполнять привычку
    time = models.TimeField()

    # Действие — действие, которое представляет собой привычку
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


class UserProfile(models.Model):
    """Дополнительный профиль пользователя для интеграции с Telegram"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram ID')
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram username')

    def __str__(self):
        return f"Профиль {self.user.email} (Telegram: {self.telegram_id or 'не указан'})"
