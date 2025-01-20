from django import forms
from .models import File
from main.models import Work


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file',)


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description']
