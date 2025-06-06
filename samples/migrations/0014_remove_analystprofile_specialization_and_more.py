# Generated by Django 5.2.1 on 2025-05-17 22:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0013_analystprofile_testassignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analystprofile',
            name='specialization',
        ),
        migrations.RemoveField(
            model_name='testassignment',
            name='assigned_at',
        ),
        migrations.RemoveField(
            model_name='testassignment',
            name='completed_at',
        ),
        migrations.RemoveField(
            model_name='testassignment',
            name='parameter',
        ),
        migrations.RemoveField(
            model_name='testassignment',
            name='remarks',
        ),
        migrations.RemoveField(
            model_name='testassignment',
            name='status',
        ),
        migrations.AddField(
            model_name='analystprofile',
            name='full_name',
            field=models.CharField(default='name', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testassignment',
            name='sub_parameter',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='testassignment',
            name='test_parameter',
            field=models.CharField(choices=[('proximate', 'Proximate'), ('gross_energy', 'Gross Energy'), ('aflatoxin', 'Aflatoxin'), ('vitamins', 'Vitamins'), ('water_analysis', 'Water Analysis'), ('microbial_analysis', 'Microbial Analysis')], default='param', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sample',
            name='test_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='samples.testrequest'),
        ),
        migrations.AlterField(
            model_name='testassignment',
            name='deadline',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='testassignment',
            name='result',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testassignment',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='samples.sample'),
        ),
        migrations.AlterField(
            model_name='testrequest',
            name='analysis_types',
            field=models.CharField(choices=[('proximate', 'Proximate'), ('aflatoxin', 'Aflatoxin'), ('gross_energy', 'Gross Energy'), ('metabolizable_energy', 'Metabolizable Energy'), ('vitamins', 'Vitamins')], max_length=255),
        ),
        migrations.AlterField(
            model_name='testrequest',
            name='name_of_receiver',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]
