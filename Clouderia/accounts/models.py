from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_profile')
    avatar = models.ImageField(upload_to='avatars/', default='default_avatar.png')
    work_email = models.EmailField(blank=True, null=True, default='')
    total_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
