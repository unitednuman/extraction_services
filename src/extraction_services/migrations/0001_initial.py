# Generated by Django 2.2.16 on 2022-05-18 05:25

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HouseAuction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('version', models.IntegerField()),
                ('property_description', models.TextField()),
                ('address', models.CharField(max_length=255)),
                ('postal_code', models.IntegerField()),
                ('number_of_bedrooms', models.IntegerField()),
                ('property_type', models.CharField(max_length=255)),
                ('tenure', models.TextField()),
                ('auction_date', models.DateField()),
                ('auction_hour', models.TimeField()),
                ('domain', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
