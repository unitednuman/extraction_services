# Generated by Django 3.2.13 on 2022-08-13 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extraction_services", "0002_errorreport_secondary_error"),
    ]

    operations = [
        migrations.AddField(
            model_name="houseauction",
            name="is_sold",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
