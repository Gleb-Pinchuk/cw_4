from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from habits.models import Habit


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(8, 0),
            action="Пить воду",
            is_pleasant=False,
            frequency=1,
            duration=1,
            is_public=True,
        )

    def test_habit_creation(self):
        """Проверка создания привычки"""
        self.assertEqual(self.habit.action, "Пить воду")
        self.assertEqual(self.habit.user.username, "testuser")
        self.assertEqual(self.habit.is_public, True)

    def test_habit_string_representation(self):
        """Проверка строкового представления"""
        self.assertEqual(str(self.habit), "Привычка: Пить воду (testuser)")

    def test_pleasant_habit_cannot_have_reward(self):
        """Приятная привычка не может иметь вознаграждение"""
        pleasant = Habit(
            user=self.user,
            time=time(9, 0),
            action="Отдых",
            is_pleasant=True,
            duration=1,
            reward="Не должно быть",
        )
        with self.assertRaises(Exception):
            pleasant.full_clean()

    def test_pleasant_habit_cannot_have_related(self):
        """Приятная привычка не может иметь связанную привычку"""
        pleasant = Habit(
            user=self.user,
            time=time(9, 0),
            action="Отдых",
            is_pleasant=True,
            duration=1,
            related_habit=self.habit,
        )
        with self.assertRaises(Exception):
            pleasant.full_clean()

    def test_useful_habit_cannot_have_both_reward_and_related(self):
        """Полезная привычка не может иметь и вознаграждение, и связанную привычку"""
        related_pleasant = Habit.objects.create(
            user=self.user,
            time=time(10, 0),
            action="Приятное",
            is_pleasant=True,
            duration=1,
        )
        useful = Habit(
            user=self.user,
            time=time(8, 30),
            action="Зарядка",
            is_pleasant=False,
            duration=1,
            reward="Десерт",
            related_habit=related_pleasant,
        )
        with self.assertRaises(Exception):
            useful.full_clean()

    def test_related_habit_must_be_pleasant(self):
        """Связанная привычка должна быть приятной"""
        not_pleasant = Habit.objects.create(
            user=self.user,
            time=time(11, 0),
            action="Работа",
            is_pleasant=False,
            duration=1,
        )
        useful = Habit(
            user=self.user,
            time=time(8, 30),
            action="Зарядка",
            is_pleasant=False,
            duration=1,
            related_habit=not_pleasant,
        )
        with self.assertRaises(Exception):
            useful.full_clean()

    def test_frequency_max_7_days(self):
        """Частота не может быть больше 7 дней"""
        habit = Habit(
            user=self.user,
            time=time(8, 0),
            action="Редкая привычка",
            frequency=10,  # Больше 7
            duration=1,
        )
        with self.assertRaises(Exception):
            habit.full_clean()

    def test_duration_max_2_minutes(self):
        """Время выполнения не больше 2 минут"""
        habit = Habit(
            user=self.user,
            time=time(8, 0),
            action="Долгая привычка",
            duration=5,  # Больше 2
        )
        with self.assertRaises(Exception):
            habit.full_clean()


class HabitAPITest(APITestCase):
    """Тесты для API эндпоинтов"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="apiuser", password="apipass123")
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.habit = Habit.objects.create(
            user=self.user,
            place="Офис",
            time=time(9, 0),
            action="План на день",
            frequency=1,
            duration=2,
            is_public=False,
        )
        self.public_habit = Habit.objects.create(
            user=User.objects.create_user(username="other", password="pass"),
            place="Парк",
            time=time(7, 0),
            action="Пробежка",
            frequency=1,
            duration=2,
            is_public=True,
        )

    def test_list_habits_authenticated(self):
        """Авторизованный пользователь видит свои + публичные привычки"""
        url = reverse("habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_pagination(self):
        """Проверка пагинации (5 элементов на страницу)"""
        # Создаём ещё 6 привычек (всего станет 8)
        for i in range(6):
            Habit.objects.create(
                user=self.user, time=time(8, i), action=f"Привычка {i}", duration=1
            )
        url = reverse("habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # PAGE_SIZE = 5
        self.assertIsNotNone(response.data["next"])  # Есть следующая страница

    def test_create_habit(self):
        """Создание новой привычки"""
        url = reverse("habits-list")
        data = {
            "place": "Дома",
            "time": "08:00:00",
            "action": "Новая привычка",
            "frequency": 1,
            "duration": 1,
            "is_public": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)  # Было 2, стало 3
        self.assertEqual(response.data["action"], "Новая привычка")
        self.assertEqual(
            response.data["user"], self.user.id
        )  # User assigned automatically

    def test_update_habit(self):
        """Редактирование своей привычки"""
        url = reverse("habits-detail", args=[self.habit.id])
        data = {"action": "Обновлённое действие"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "Обновлённое действие")

    def test_delete_habit(self):
        """Удаление своей привычки"""
        url = reverse("habits-detail", args=[self.habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)  # Осталась только публичная

    def test_cannot_delete_other_user_habit(self):
        """Нельзя удалить чужую непубличную привычку"""
        private_other = Habit.objects.create(
            user=User.objects.create_user(username="other2", password="pass"),
            time=time(10, 0),
            action="Чужая",
            duration=1,
            is_public=False,
        )
        url = reverse("habits-detail", args=[private_other.id])
        response = self.client.delete(url)
        # Привычка не в списке пользователя, поэтому 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_view_public_habits(self):
        """Можно видеть публичные привычки других пользователей"""
        url = reverse("habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В результатах должна быть публичная привычка
        actions = [h["action"] for h in response.data["results"]]
        self.assertIn("Пробежка", actions)

    def test_unauthenticated_access_denied(self):
        """Неавторизованный доступ запрещён"""
        self.client.credentials()  # Убираем токен
        url = reverse("habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthAPITest(APITestCase):
    """Тесты для регистрации и авторизации"""

    def test_register_user(self):
        """Регистрация нового пользователя"""
        url = reverse("register")
        data = {"username": "newuser", "password": "newpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_user(self):
        """Авторизация существующего пользователя"""
        User.objects.create_user(username="loginuser", password="loginpass")
        url = reverse("login")
        data = {"username": "loginuser", "password": "loginpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_wrong_password(self):
        """Неверный пароль при входе"""
        User.objects.create_user(username="testuser", password="correctpass")
        url = reverse("login")
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
