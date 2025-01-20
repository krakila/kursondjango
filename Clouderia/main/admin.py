from django.contrib import admin
from .models import Work, Complaint, Comment
from accounts.models import UserProfile

# Регистрация моделей
admin.site.register(Work)
admin.site.register(Complaint)
admin.site.register(Comment)
admin.site.register(UserProfile)