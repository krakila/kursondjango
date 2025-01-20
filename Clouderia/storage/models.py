from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile  # Убедитесь, что импорт правильный

def user_directory_path(instance, filename):
    return f'uploads/{instance.user.user.username}/{instance.title}/{filename}'

class File(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    folder_path = models.CharField(max_length=1024, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    likes = models.ManyToManyField(UserProfile, related_name='liked_files', blank=True)
    dislikes = models.ManyToManyField(UserProfile, related_name='disliked_files', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(null=True, blank=True)  # Размер в байтах
    file_type = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Автоматически сохраняем размер и тип файла
        if self.file:
            self.size = self.file.size
            self.file_type = self.file.name.split('.')[-1]
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return self.title

class StorageFile(models.Model):
    title = models.CharField(max_length=255)

