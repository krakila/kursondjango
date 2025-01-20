from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.test import Client
import uuid


class UserFormTest(TestCase):

    def test_user_creation_form_valid(self):
        """Тестирование валидной формы регистрации"""
        form_data = {
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_creation_form_invalid(self):
        """Тестирование невалидной формы регистрации (пароли не совпадают)"""
        form_data = {'username': 'newuser', 'password1': '12345', 'password2': 'wrongpassword'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_authentication_form_valid(self):
        """Тестирование валидной формы аутентификации"""
        user = User.objects.create_user(username='testuser', password='12345')
        form_data = {'username': 'testuser', 'password': '12345'}
        form = AuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_authentication_form_invalid(self):
        """Тестирование невалидной формы аутентификации"""
        form_data = {'username': 'testuser', 'password': 'wrongpassword'}
        form = AuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_login_view_get(self):
        """Проверка правильности отображения формы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_post_valid(self):
        """Проверка входа с правильными данными"""
        user = User.objects.create_user(username='testuser', password='12345')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertRedirects(response, reverse('main_page'))

    def test_register_view_get(self):
        """Проверка правильности отображения формы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')



class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile, created = UserProfile.objects.get_or_create(user=self.user,
                                                                  defaults={'work_email': "testuser@example.com"})

    def test_str_method(self):
        """Проверка метода __str__ модели UserProfile"""
        self.assertEqual(str(self.profile), 'testuser')


class SignalTest(TestCase):

    def test_create_profile_signal(self):
        """Проверка сигнала для создания профиля при создании пользователя"""
        user = User.objects.create_user(username='newuser', password='12345')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user.username, 'newuser')
