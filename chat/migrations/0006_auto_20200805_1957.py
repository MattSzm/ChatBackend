# Generated by Django 3.0.8 on 2020-08-05 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20200728_1945'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='last_message_date',
            new_name='last_activity_date',
        ),
    ]
