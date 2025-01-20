from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile only if it's new user
        UserProfile.objects.create(user=instance)
        print(f"Профиль создан для пользователя {instance.username}")
    else:
        # If profile exists, save it
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if not created:  # If it exists, just save it
            profile.save()
        print(f"Профиль обновлен для пользователя {instance.username}")
