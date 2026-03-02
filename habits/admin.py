from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from habits.models import User, Habit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_staff', 'is_active', 'telegram_id')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'telegram_id')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Telegram', {'fields': ('telegram_id', 'telegram_username')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'time', 'is_pleasant', 'is_public', 'frequency')
    list_filter = ('is_public', 'is_pleasant', 'user')
    search_fields = ('action', 'place', 'user__email')
