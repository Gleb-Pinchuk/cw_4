from django.contrib import admin

from habits.models import Habit, UserProfile


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "time", "is_pleasant", "is_public")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_id", "telegram_username")
