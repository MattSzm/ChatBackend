# Generated by Django 3.0.8 on 2020-07-28 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20200726_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='last_message_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
