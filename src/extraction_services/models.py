from django.db import models
from model_utils.models import TimeStampedModel
from datetime import timedelta
from django.utils.timezone import now
import django
import datetime
import pytz


# Create your models here.
class HouseAuction(TimeStampedModel):
    guide_price = models.CharField(max_length=255, null=True, blank=True)
    picture_link = models.CharField(max_length=255, null=True, blank=True)
    property_description = models.TextField()
    property_link: models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    number_of_bedrooms = models.CharField(max_length=255, null=True, blank=True)
    property_type = models.CharField(max_length=255, null=True, blank=True)
    tenure = models.TextField()
    auction_date = models.CharField(max_length=255, null=True, blank=True)
    auction_hour = models.CharField(max_length=255, null=True, blank=True)
    auction_venue = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
