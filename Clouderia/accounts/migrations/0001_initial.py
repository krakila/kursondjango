# Generated by Django 5.1.3 on 2024-12-06 14:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(default='default_avatar.png', upload_to='avatars/')),
                ('work_email', models.EmailField(blank=True, default='', max_length=254, null=True)),
                ('total_likes', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='accounts_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
