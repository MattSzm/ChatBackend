# Generated by Django 3.0.8 on 2020-07-28 19:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20200728_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='last_message_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
