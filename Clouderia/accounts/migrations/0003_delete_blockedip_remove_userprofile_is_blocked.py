# Generated by Django 5.1.3 on 2024-12-06 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_blockedip_userprofile_is_blocked'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BlockedIP',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_blocked',
        ),
    ]
