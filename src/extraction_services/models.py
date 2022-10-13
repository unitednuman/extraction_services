import inspect
import logging
import os
import re
from datetime import timedelta
from threading import Thread
from django.core.exceptions import SynchronousOnlyOperation
from django.db import models
from django.utils.html import strip_tags
from model_utils.models import TimeStampedModel
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

logging.basicConfig(format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s", level=logging.DEBUG)


def disable_other_loggers():
    for name in logging.root.manager.loggerDict:
        # print("logger", name)
        logging.getLogger(name).disabled = True


class LoggerModel(models.Model):
    db_log_level = logging.INFO
    level_name = models.CharField(max_length=20)
    message = models.TextField()
    created = models.DateTimeField()
    additional_info = models.JSONField()
    no_delete = models.BooleanField(default=False)

    @classmethod
    def log(cls, level_name, message, no_delete=False, **kwargs):
        level = logging._nameToLevel.get(level_name)  # noqa  # pylint: disable=protected-access
        if kwargs.get("filenames") is None:
            try:
                filenames = ", ".join(
                    {os.path.basename(s.filename) for s in inspect.stack() if r"scrappers" in s.filename}
                )
            except Exception as e:
                LoggerModel.debug(f"error while fetching filenames: {e}", filenames="")
                filenames = ""
            kwargs["filenames"] = filenames
        else:
            filenames = kwargs["filenames"]
        message = f"{filenames}: {message}"
        logging.log(level, message)
        if level >= cls.db_log_level:
            Thread(
                target=lambda: cls.objects.create(
                    level_name=level_name,
                    message=message,
                    no_delete=no_delete,
                    created=timezone.now(),
                    additional_info=kwargs,
                ),
                daemon=True,
            ).start()

    @classmethod
    def info(cls, message, no_delete=False, **kwargs):
        cls.log("INFO", message, no_delete=no_delete, **kwargs)

    @classmethod
    def debug(cls, message, **kwargs):
        cls.log("DEBUG", message, **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        cls.log("ERROR", message, **kwargs)

    @classmethod
    def warning(cls, message, **kwargs):
        cls.log("INFO", message, **kwargs)

    @classmethod
    def delete_previous_logs(cls):
        dt = timezone.now() - timedelta(days=10)
        del_count = cls.objects.filter(no_delete=False, created__lte=dt).delete()
        cls.info(f"deleted {del_count} logs, those were created__lte={dt}.", logs_del_count=del_count)


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
    auction_datetime = models.DateTimeField()
    auction_venue = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    # is_sold = models.BooleanField(null=True, blank=True)

    @classmethod
    def sv_upd_result_thread(cls, data: dict, async_error=False) -> "HouseAuction":
        results = []
        t = Thread(
            target=cls._sv_upd_result,
            daemon=True,
            args=(data, results),
            kwargs=dict(
                async_error=async_error,
                filenames=", ".join(
                    {os.path.basename(s.filename) for s in inspect.stack() if r"scrappers" in s.filename}
                ),
            ),
        )
        t.start()
        t.join()
        return results[0]

    @classmethod
    def sv_upd_result(cls, data: dict) -> "HouseAuction":
        try:
            return cls._sv_upd_result(data)
        except SynchronousOnlyOperation:
            return cls.sv_upd_result_thread(data, async_error=True)

    @classmethod
    def _sv_upd_result(cls, data: dict, results: list = None, async_error=False, filenames=None) -> "HouseAuction":
        if async_error:
            LoggerModel.debug("Retrying using thread", filenames=filenames)
        else:
            LoggerModel.debug("Saving HouseAuction", filenames=filenames)
        data["property_link"] = data["property_link"].strip()
        if house_auction := HouseAuction.objects.filter(property_link=data["property_link"]).first():
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
