from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from habits.models import Habit, User
from datetime import time


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(8, 0),
            action='Пить воду',
            is_pleasant=False,
            frequency=1,
            duration=1,
            is_public=True
        )

    def test_habit_creation(self):
        """Проверка создания привычки"""
        self.assertEqual(self.habit.action, 'Пить воду')
        self.assertEqual(self.habit.user.email, 'test@example.com')
        self.assertEqual(self.habit.is_public, True)

    def test_habit_string_representation(self):
        """Проверка строкового представления"""
        self.assertEqual(str(self.habit), 'Привычка: Пить воду (test@example.com)')

    def test_pleasant_habit_cannot_have_reward(self):
        """Приятная привычка не может иметь вознаграждение"""
        pleasant = Habit(
            user=self.user,
            time=time(9, 0),
            action='Отдых',
            is_pleasant=True,
            duration=1,
            reward='Не должно быть'
        )
        with self.assertRaises(Exception):
            pleasant.full_clean()

    def test_pleasant_habit_cannot_have_related(self):
        """Приятная привычка не может иметь связанную привычку"""
        pleasant = Habit(
            user=self.user,
            time=time(9, 0),
            action='Отдых',
            is_pleasant=True,
            duration=1,
            related_habit=self.habit
        )
        with self.assertRaises(Exception):
            pleasant.full_clean()

    def test_useful_habit_cannot_have_both_reward_and_related(self):
        """Полезная привычка не может иметь и вознаграждение, и связанную привычку"""
        related_pleasant = Habit.objects.create(
            user=self.user,
            time=time(10, 0),
            action='Приятное',
            is_pleasant=True,
            duration=1
        )
        useful = Habit(
            user=self.user,
            time=time(8, 30),
            action='Зарядка',
            is_pleasant=False,
            duration=1,
            reward='Десерт',
            related_habit=related_pleasant
        )
        with self.assertRaises(Exception):
            useful.full_clean()

    def test_related_habit_must_be_pleasant(self):
        """Связанная привычка должна быть приятной"""
        not_pleasant = Habit.objects.create(
            user=self.user,
            time=time(11, 0),
            action='Работа',
            is_pleasant=False,
            duration=1
        )
        useful = Habit(
            user=self.user,
            time=time(8, 30),
            action='Зарядка',
            is_pleasant=False,
            duration=1,
            related_habit=not_pleasant
        )
        with self.assertRaises(Exception):
            useful.full_clean()

    def test_frequency_max_7_days(self):
        """Частота не может быть больше 7 дней"""
        habit = Habit(
            user=self.user,
            time=time(8, 0),
            action='Редкая привычка',
            frequency=10,
            duration=1
        )
        with self.assertRaises(Exception):
            habit.full_clean()

    def test_duration_max_2_minutes(self):
        """Время выполнения не больше 2 минут"""
        habit = Habit(
            user=self.user,
            time=time(8, 0),
            action='Долгая привычка',
            duration=5
        )
        with self.assertRaises(Exception):
            habit.full_clean()


class HabitAPITest(APITestCase):
    """Тесты для API эндпоинтов"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='api@example.com', password='apipass123')
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.habit = Habit.objects.create(
            user=self.user,
            place='Офис',
            time=time(9, 0),
            action='План на день',
            frequency=1,
            duration=2,
            is_public=False
        )
        self.public_habit = Habit.objects.create(
            user=User.objects.create_user(email='other@example.com', password='pass'),
            place='Парк',
            time=time(7, 0),
            action='Пробежка',
            frequency=1,
            duration=2,
            is_public=True
        )

    def test_list_habits_authenticated(self):
        """Авторизованный пользователь видит свои привычки"""
        url = reverse('habits-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_pagination(self):
        """Проверка пагинации (5 элементов на страницу)"""
        for i in range(6):
            Habit.objects.create(
                user=self.user,
                time=time(8, i),
                action=f'Привычка {i}',
                duration=1
            )
        url = reverse('habits-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])

    def test_create_habit(self):
        """Создание новой привычки"""
        url = reverse('habits-list')
        data = {
            'place': 'Дома',
            'time': '08:00:00',
            'action': 'Новая привычка',
            'frequency': 1,
            'duration': 1,
            'is_public': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Новая привычка')
        self.assertEqual(response.data['user'], self.user.id)

    def test_update_habit(self):
        """Редактирование своей привычки"""
        url = reverse('habits-detail', args=[self.habit.id])
        data = {'action': 'Обновлённое действие'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, 'Обновлённое действие')

    def test_delete_habit(self):
        """Удаление своей привычки"""
        url = reverse('habits-detail', args=[self.habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)

    def test_cannot_delete_other_user_habit(self):
        """Нельзя удалить чужую непубличную привычку"""
        private_other = Habit.objects.create(
            user=User.objects.create_user(email='other2@example.com', password='pass'),
            time=time(10, 0),
            action='Чужая',
            duration=1,
            is_public=False
        )
        url = reverse('habits-detail', args=[private_other.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_view_public_habits(self):
        """Можно видеть публичные привычки других пользователей"""
        url = reverse('habits-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access_denied(self):
        """Неавторизованный доступ запрещён"""
        self.client.credentials()
        url = reverse('habits-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthAPITest(APITestCase):
    """Тесты для регистрации и авторизации"""

    def setUp(self):
        """Создаём пользователя и токен для тестов"""
        self.user = User.objects.create_user(email='auth@example.com', password='authpass123')
        self.refresh = RefreshToken.for_user(self.user)

    def test_register_user(self):
        """Регистрация нового пользователя"""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_user(self):
        """Авторизация существующего пользователя"""
        url = reverse('login')
        data = {
            'email': 'auth@example.com',
            'password': 'authpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_wrong_password(self):
        """Неверный пароль при входе"""
        url = reverse('login')
        data = {
            'email': 'auth@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_token_refresh(self):
        """Обновление токена"""
        url = reverse('token_refresh')
        data = {'refresh': str(self.refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
