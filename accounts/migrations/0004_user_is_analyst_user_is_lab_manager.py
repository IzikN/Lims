# Generated by Django 4.2.19 on 2025-05-13 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_staff_name_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_analyst',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_lab_manager',
            field=models.BooleanField(default=False),
        ),
    ]
