# Generated by Django 4.2.5 on 2023-09-17 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_message_type_youtubevideo_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='type',
            new_name='message_type',
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='script',
            field=models.TextField(blank=True, null=True, verbose_name='Script'),
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='tags',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Tags'),
        ),
    ]
