# Generated by Django 3.2.13 on 2022-09-17 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extraction_services', '0006_rename_level_loggermodel_level_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='loggermodel',
            name='no_delete',
            field=models.BooleanField(default=False),
        ),
    ]
