# Generated by Django 3.2.13 on 2022-06-09 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extraction_services', '0010_errorreport_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errorreport',
            name='error',
            field=models.TextField(blank=True, null=True),
        ),
    ]
