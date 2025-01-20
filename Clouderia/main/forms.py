from django import forms
from .models import Work
from .models import Report
from accounts.models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description', 'file']



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'work_email']

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Текущий пароль неверен.")
        return old_password