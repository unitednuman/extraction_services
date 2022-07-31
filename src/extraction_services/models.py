import inspect
import logging
import os
import re
from threading import Thread
from django.core.exceptions import SynchronousOnlyOperation
from django.db import models
from django.utils.html import strip_tags
from model_utils.models import TimeStampedModel
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

    @classmethod
    def sv_upd_result(cls, data: dict) -> "HouseAuction":
        try:
            return cls._sv_upd_result(data)
        except SynchronousOnlyOperation:
            results = []
            t = Thread(target=cls._sv_upd_result, daemon=True, args=(data, results))
            t.start()
            t.join()
            return results[0]

    @classmethod
    def _sv_upd_result(cls, data: dict, results: list = None) -> "HouseAuction":
        try:
            filenames = ", ".join([os.path.basename(s.filename) for s in inspect.stack()])
        except:
            filenames = ""
        logging.info(f"{filenames}: Saving HouseAuction")
        data['property_link'] = data['property_link'].strip()
        if house_auction := HouseAuction.objects.filter(property_link=data['property_link']).first():
            house_auction.__dict__.update(data)
        else:
            house_auction = HouseAuction(**data)
        house_auction.save()
        if results is not None:
            results.append(house_auction)
        return house_auction


@receiver(pre_save, sender=HouseAuction)
def pre_save_validator(sender, instance, **kwargs):
    if instance.property_description:
        instance.property_description = strip_tags(instance.property_description).strip()
    if instance.currency_type:
        instance.currency_type = instance.currency_type.strip()
    if instance.picture_link:
        instance.picture_link = instance.picture_link.strip()
    if instance.address:
        instance.address = instance.address.strip()
    if instance.postal_code:
        instance.postal_code = instance.postal_code.strip()
    if instance.property_type:
        instance.property_type = instance.property_type.strip()
    if instance.tenure:
        instance.tenure = strip_tags(instance.tenure).strip()
    if instance.auction_venue:
        instance.auction_venue = instance.auction_venue.strip()
    if instance.source:
        instance.source = instance.source.strip()
    if isinstance(instance.number_of_bedrooms, str):
        if match := re.search(r"(\d+) Bedrooms?", instance.number_of_bedrooms):
            instance.number_of_bedrooms = int(match.group(1))
    elif not isinstance(instance.number_of_bedrooms, int):
        instance.number_of_bedrooms = None


# pre_save.connect(pre_save_validator,sender=HouseAuction)


class ErrorReport(TimeStampedModel):
    file_name = models.CharField(max_length=255, null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    trace_back = models.TextField(null=True, blank=True)
    count = models.IntegerField(default=1)
    secondary_error = models.BooleanField(default=False)
