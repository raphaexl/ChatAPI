# Generated by Django 4.2.5 on 2023-09-16 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_youtubevideo_remove_conversation_receiver_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('timestamp',)},
        ),
        migrations.AddField(
            model_name='message',
            name='is_from_user',
            field=models.BooleanField(default=True),
        ),
    ]
