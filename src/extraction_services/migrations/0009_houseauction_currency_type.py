# Generated by Django 2.2.16 on 2022-05-28 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extraction_services', '0008_auto_20220521_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='houseauction',
            name='currency_type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]