from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
from storage.models import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from storage.models import File
from accounts.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from main.forms import UploadFileForm
from django.test import TestCase
from storage.utils import get_file_type
from django.core.files.uploadedfile import SimpleUploadedFile

class FileTypeUtilityTest(TestCase):

    def test_get_file_type_image(self):
        file = SimpleUploadedFile("test_image.jpg", b"image_content", content_type="image/jpeg")
        file_type = get_file_type(file)
        self.assertEqual(file_type, "image")

    def test_get_file_type_pdf(self):
        file = SimpleUploadedFile("test_document.pdf", b"pdf_content", content_type="application/pdf")
        file_type = get_file_type(file)
        self.assertEqual(file_type, "pdf")

    def test_get_file_type_unknown(self):
        file = SimpleUploadedFile("test_file.txt", b"text_content", content_type="text/plain")
        file_type = get_file_type(file)
        self.assertEqual(file_type, "other")

class UploadFileFormTest(TestCase):

    def test_form_valid(self):
        form_data = {
            'title': 'Test File',
            'description': 'Test Description'
        }
        form = UploadFileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'title': '',  # Missing title to trigger validation error
            'description': 'Test Description'
        }
        form = UploadFileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

