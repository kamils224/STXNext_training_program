# Generated by Django 3.1.5 on 2021-01-20 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issueattachment',
            old_name='file_name',
            new_name='file_attachment',
        ),
    ]