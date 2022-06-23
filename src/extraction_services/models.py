from django.db import models
from model_utils.models import TimeStampedModel
from datetime import timedelta
from django.utils.timezone import now
import django
import datetime
import pytz
from django.db.models.signals import pre_save
from django.dispatch import receiver


# Create your models here.
class HouseAuction(TimeStampedModel):
    price = models.FloatField(null=True, blank=True)
    currency_type = models.CharField(max_length=10, null=True, blank=True)
    picture_link = models.TextField(null=True, blank=True)
    property_description = models.TextField(null=True, blank=True)
    property_link = models.TextField(null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    number_of_bedrooms = models.IntegerField(null=True, blank=True)
    property_type = models.TextField(null=True, blank=True)
    tenure = models.TextField(null=True, blank=True)
    auction_datetime = models.DateTimeField(null=True, blank=True)
    auction_venue = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)


@receiver(pre_save, sender=HouseAuction)
def pre_save_validator(sender, instance, **kwargs):
    if instance.property_description:
        instance.property_description = instance.property_description.strip()
    if instance.currency_type:
        instance.currency_type = instance.currency_type.strip()
    if instance.picture_link:
        instance.picture_link = instance.picture_link.strip()
    if instance.property_link:
        instance.property_link = instance.property_link.strip()
    if instance.address:
        instance.address = instance.address.strip()
    if instance.postal_code:
        instance.postal_code = instance.postal_code.strip()
    if instance.property_type:
        instance.property_type = instance.property_type.strip()
    if instance.tenure:
        instance.tenure = instance.tenure.strip()
    if instance.auction_venue:
        instance.auction_venue = instance.auction_venue.strip()
    if instance.source:
        instance.source = instance.source.strip()




# pre_save.connect(pre_save_validator,sender=HouseAuction)


class ErrorReport(TimeStampedModel):
    file_name = models.CharField(max_length=255, null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    trace_back = models.TextField(null=True, blank=True)
    count = models.IntegerField(default=1)
