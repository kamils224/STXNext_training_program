# Generated by Django 3.1.5 on 2021-01-19 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='task_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
