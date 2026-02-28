from django.contrib.auth.models import User
from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычки"""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)

    def validate(self, data):
        is_pleasant = data.get("is_pleasant", False)
        reward = data.get("reward")
        related_habit = data.get("related_habit")

        if is_pleasant:
            if reward:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения."
                )
            if related_habit:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть связанной привычки."
                )
        else:
            if reward and related_habit:
                raise serializers.ValidationError(
                    "Нельзя одновременно указать вознаграждение и связанную привычку."
                )

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной."
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""

    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
