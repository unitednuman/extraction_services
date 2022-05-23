# Generated by Django 2.2.16 on 2022-05-21 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extraction_services', '0004_auto_20220521_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='houseauction',
            name='auction_date',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='houseauction',
            name='auction_hour',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='houseauction',
            name='number_of_bedrooms',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='houseauction',
            name='postal_code',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='houseauction',
            name='price',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='houseauction',
            name='property_type',
            field=models.TextField(blank=True, null=True),
        ),
    ]
