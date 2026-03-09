from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя (регистрация)"""

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'telegram_id', 'telegram_username')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для входа по email"""

    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['user_id'] = self.user.id
        return data
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email:
            raise serializers.ValidationError('Email обязателен')
        if not password:
            raise serializers.ValidationError('Пароль обязателен')
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['user_id'] = self.user.id

        return data
