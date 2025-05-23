# Generated by Django 3.2 on 2025-05-10 22:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_id', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('sample_type', models.CharField(choices=[('food', 'Food'), ('feed', 'Feed'), ('water', 'Water'), ('ingredient', 'Raw Material'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('date_received', models.DateField()),
                ('is_urgent', models.BooleanField(default=False)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_samples', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TestRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tests_required', models.TextField(help_text='Comma-separated test names')),
                ('date_requested', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('sample', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='samples.sample')),
            ],
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='attachments/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('label', models.CharField(blank=True, max_length=100)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='samples.sample')),
            ],
        ),
    ]
