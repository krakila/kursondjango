# Generated by Django 5.1.3 on 2024-12-06 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='is_blocked',
        ),
    ]
