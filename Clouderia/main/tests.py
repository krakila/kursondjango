from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
from main.models import Work, Comment, Complaint
from django.test import TestCase
from main.forms import UploadFileForm, UserProfileForm, CustomPasswordChangeForm
from accounts.models import UserProfile
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Work, UserProfile
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import upload_file, main_page, view_work

class URLTestCase(SimpleTestCase):
    def test_upload_file_url_resolves(self):
        url = reverse('upload_file')
        self.assertEqual(resolve(url).func, upload_file)

    def test_main_page_url_resolves(self):
        url = reverse('main_page')
        self.assertEqual(resolve(url).func, main_page)

    def test_view_work_url_resolves(self):
        url = reverse('view_work', args=[1])
        self.assertEqual(resolve(url).func, view_work)

class ViewsTestCase(TestCase):
    def setUp(self):
        # Создаем пользователя и авторизуем его
        self.user = User.objects.create_user(username='testuser1', password='testpassword')
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.client = Client()
        self.client.login(username='testuser1', password='testpassword')

        # Создаем тестовую работу
        self.work = Work.objects.create(
            title="Test Work",
            description="This is a test work",
            user=self.user_profile
        )

    def test_upload_file_view(self):
        response = self.client.get(reverse('upload_file'))
        self.assertEqual(response.status_code, 200)

    def test_view_work(self):
        response = self.client.get(reverse('view_work', args=[self.work.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.work.title)

    def test_like_work(self):
        response = self.client.post(reverse('like_work', args=[self.work.id]))
        self.assertEqual(response.status_code, 200)
        self.work.refresh_from_db()
        self.assertEqual(self.work.total_likes(), 1)

    def test_dislike_work(self):
        response = self.client.post(reverse('dislike_work', args=[self.work.id]))
        self.assertEqual(response.status_code, 200)
        self.work.refresh_from_db()
        self.assertEqual(self.work.total_dislikes(), 1)

class FormsTestCase(TestCase):
    def test_upload_file_form_valid(self):
        form_data = {
            'title': 'Test Title',
            'description': 'Test Description',
        }
        form = UploadFileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_profile_form_valid(self):
        form_data = {
            'avatar': None,
            'work_email': 'test@example.com',
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_change_form_invalid(self):
        user = User.objects.create_user(username='testuser2', password='testpassword')
        form_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newstrongpassword',
            'new_password2': 'newstrongpassword',
        }
        form = CustomPasswordChangeForm(user=user, data=form_data)
        self.assertFalse(form.is_valid())


class ModelsTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser3', password='testpassword')

        # Check if UserProfile exists, and create it if it doesn't
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)

        # Создаем тестовую работу
        self.work = Work.objects.create(
            title="Test Work",
            description="This is a test work",
            user=self.user_profile
        )

    def test_work_creation(self):
        self.assertEqual(self.work.title, "Test Work")
        self.assertEqual(self.work.user, self.user_profile)

    def test_work_likes_dislikes(self):
        self.work.likes.add(self.user_profile)
        self.assertEqual(self.work.total_likes(), 1)

        self.work.dislikes.add(self.user_profile)
        self.assertEqual(self.work.total_dislikes(), 1)

    def test_comment_creation(self):
        comment = Comment.objects.create(
            work=self.work,
            user=self.user_profile,
            content="Test comment"
        )
        self.assertEqual(comment.content, "Test comment")
        self.assertEqual(comment.work, self.work)

    def test_complaint_creation(self):
        complaint = Complaint.objects.create(
            reporter=self.user_profile,
            reported_work=self.work,
            reason="Inappropriate content"
        )
        self.assertEqual(complaint.reason, "Inappropriate content")
