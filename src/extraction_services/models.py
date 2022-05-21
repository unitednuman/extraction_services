from django.db import models
from model_utils.models import TimeStampedModel
from datetime import timedelta
from django.utils.timezone import now
import django
import datetime
import pytz


# Create your models here.
class HouseAuction(TimeStampedModel):
    price = models.FloatField(null=True, blank=True)
    picture_link = models.TextField(null=True, blank=True)
    property_description = models.TextField(null=True, blank=True)
    property_link = models.TextField(null=True, blank=True , unique=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    number_of_bedrooms = models.TextField(null=True, blank=True)
    property_type = models.TextField(null=True, blank=True)
    tenure = models.TextField(null=True, blank=True)
    auction_datetime = models.DateTimeField(null=True, blank=True)
    auction_venue = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)


class ErrorReport(TimeStampedModel):
    file_name = models.CharField(max_length=255, null=True, blank=True)
    error = models.CharField(max_length=255, null=True, blank=True)
    trace_back = models.TextField(null=True, blank=True)
