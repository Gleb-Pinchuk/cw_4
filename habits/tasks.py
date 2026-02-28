import logging
from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from habits.models import Habit, UserProfile

logger = logging.getLogger(__name__)


@shared_task
def send_reminder_notifications():
    """
    Периодическая задача: проверяет привычки и отправляет напоминания в Telegram
    Запускается каждые 60 секунд через celery-beat
    """
    now = timezone.now()
    current_time = now.time()

    # Находим привычки, которые нужно выполнить сейчас (±5 минут)
    # Только для активных пользователей
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        user__is_active=True,
    ).select_related("user")

    sent_count = 0
    skipped_count = 0

    for habit in habits:
        # Получаем Telegram ID из профиля пользователя
        telegram_id = None
        try:
            if hasattr(habit.user, "profile") and habit.user.profile.telegram_id:
                telegram_id = habit.user.profile.telegram_id
        except UserProfile.DoesNotExist:
            # Профиль не создан для этого пользователя
            skipped_count += 1
            continue

        if telegram_id:
            message = (
                f"🔔 <b>Напоминание о привычке!</b>\n\n"
                f"⏰ <b>Время:</b> {habit.time.strftime('%H:%M')}\n"
                f"📍 <b>Место:</b> {habit.place or 'Не указано'}\n"
                f"✅ <b>Действие:</b> {habit.action}\n"
                f"⏱ <b>Время на выполнение:</b> {habit.duration} мин.\n"
                f"🎁 <b>Вознаграждение:</b> {habit.reward or 'Нет'}"
            )

            success = send_telegram_message(telegram_id, message)
            if success:
                sent_count += 1
                logger.info(
                    f"Отправлено напоминание пользователю {habit.user.username} (привычка: {habit.action})"
                )
            else:
                skipped_count += 1
        else:
            skipped_count += 1
            logger.debug(f"У пользователя {habit.user.username} не указан Telegram ID")

    result = f"Проверено привычек: {habits.count()}, отправлено: {sent_count}, пропущено: {skipped_count}"
    logger.info(result)
    return result


def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение в Telegram

    Args:
        chat_id: ID чата пользователя в Telegram
        text: Текст сообщения

    Returns:
        bool: True если сообщение отправлено успешно, False иначе
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN

    if not bot_token:
        logger.error("Telegram bot token not configured!")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )

        if response.status_code == 200:
            logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return True
        else:
            logger.error(
                f"Ошибка отправки в Telegram: {response.status_code} - {response.text}"
            )
            return False

    except requests.exceptions.Timeout:
        logger.error(f"Timeout при отправке сообщения в чат {chat_id}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return False


@shared_task
def send_weekly_report():
    """
    Еженедельная задача: отправляет отчёт о выполненных привычках за неделю
    (Дополнительная задача для демонстрации работы Celery)
    """
    from django.contrib.auth.models import User

    now = timezone.now()
    week_ago = now - timedelta(days=7)

    users = User.objects.filter(is_active=True)

    for user in users:
        try:
            telegram_id = None
            if hasattr(user, "profile") and user.profile.telegram_id:
                telegram_id = user.profile.telegram_id

            if telegram_id:
                completed_habits = Habit.objects.filter(
                    user=user, created_at__gte=week_ago
                ).count()

                message = (
                    f"📊 <b>Недельный отчёт</b>\n\n"
                    f"👤 Пользователь: {user.username}\n"
                    f"📅 Период: последние 7 дней\n"
                    f"✅ Создано привычек: {completed_habits}\n\n"
                    f"Продолжай в том же духе! 💪"
                )

                send_telegram_message(telegram_id, message)
                logger.info(f"Отправлен недельный отчёт пользователю {user.username}")

        except Exception as e:
            logger.error(
                f"Ошибка при отправке отчёта пользователю {user.username}: {e}"
            )

    return "Недельные отчёты отправлены"
