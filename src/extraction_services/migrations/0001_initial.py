# Generated by Django 3.2.13 on 2022-06-28 17:43

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('error', models.TextField(blank=True, null=True)),
                ('trace_back', models.TextField(blank=True, null=True)),
                ('count', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HouseAuction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('price', models.FloatField(blank=True, null=True)),
                ('currency_type', models.CharField(blank=True, max_length=10, null=True)),
                ('picture_link', models.TextField(blank=True, null=True)),
                ('property_description', models.TextField(blank=True, null=True)),
                ('property_link', models.TextField(blank=True, null=True, unique=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('postal_code', models.TextField(blank=True, null=True)),
                ('number_of_bedrooms', models.IntegerField(blank=True, null=True)),
                ('property_type', models.TextField(blank=True, null=True)),
                ('tenure', models.TextField(blank=True, null=True)),
                ('auction_datetime', models.DateTimeField(blank=True, null=True)),
                ('auction_venue', models.TextField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
