from django.db import models
# from user_service.models import User
from model_utils.models import TimeStampedModel
# from utils.file_utils import upload_user_media
from datetime import timedelta
from django.utils.timezone import now
import django
import datetime
import pytz


# Create your models here.
class HouseAuction(TimeStampedModel):
    version = models.IntegerField()
    guide_price: models.FloatField()
    picture_link: models.CharField(max_length=255, null=False, blank=False)
    property_description = models.TextField()
    property_link: models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    postal_code = models.IntegerField()
    number_of_bedrooms = models.IntegerField()
    property_type = models.CharField(max_length=255, null=False, blank=False)
    tenure = models.TextField()
    auction_date = models.DateField()
    auction_hour = models.TimeField()
    domain = models.CharField(max_length=255, null=False, blank=False)
