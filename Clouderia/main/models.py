from django.db import models
from accounts.models import UserProfile  # Убедитесь, что импорт правильный

def user_directory_path(instance, filename):
    return f'uploads/{instance.user.user.username}/{instance.title}/{filename}'

class Work(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    folder_path = models.CharField(max_length=1024, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    likes = models.ManyToManyField(UserProfile, related_name='liked_works', blank=True)
    dislikes = models.ManyToManyField(UserProfile, related_name='disliked_works', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def total_likes(self):
        return self.likes.count()

    def update_author_likes(self):
        """Обновляет общее количество лайков у пользователя"""
        total_likes_count = sum(work.likes.count() for work in self.user.work_set.all())
        self.user.total_likes = total_likes_count
        self.user.save()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return self.title


class Report(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.work.title} by {self.user.user.username}"


class Complaint(models.Model):
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='filed_complaints')
    reported_work = models.ForeignKey('Work', on_delete=models.CASCADE, related_name='complaints')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Новая')  # Статус жалобы ('Новая', 'Рассмотрена', 'Отклонена')

    def __str__(self):
        return f'Жалоба на {self.reported_work.title} от {self.reporter.user.username}'


class Comment(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.user.user.username} на {self.work.title}'

