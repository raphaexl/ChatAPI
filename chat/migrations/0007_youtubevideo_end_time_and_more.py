# Generated by Django 4.2.5 on 2023-09-23 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_rename_type_message_message_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubevideo',
            name='end_time',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='youtubevideo',
            name='include_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='youtubevideo',
            name='include_tags',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='youtubevideo',
            name='include_title',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='youtubevideo',
            name='start_time',
            field=models.FloatField(default=0.0),
        ),
    ]