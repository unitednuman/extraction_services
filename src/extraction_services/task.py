from django_q.tasks import schedule
from django_q.models import Schedule
import arrow
from .models import AccessoriesType, Toy, ToyAccessorie, ToySetting
import django
import datetime


def update_score():
    accessories = ToyAccessorie.objects.all()
    if accessories:
        for accessory in accessories:
            if accessory.accessory_type.name == 'Hunger':
                all_accessories = ToyAccessorie.objects.filter(toy_id=accessory.toy.id)
                toy = Toy.objects.filter(id=accessory.toy.id).first()
                if accessory.health_status > 0:
                    points = 0.0
                    for acc in all_accessories:
                        points = points + acc.health_status / 100
                    points = points / 4
                    points = float(toy.level.level) * points
                    toy.points_per_minute = round(points, 2)
                    points = points * 60.0
                    toy.points = round(toy.points + points, 2)
                    toy.save()
                else:
                    toy.points_per_minute = 0
                    toy.save()

            if accessory.health_status > 0:
                try:
                    last_scan_datetime = datetime.datetime.strptime(str(accessory.last_scan).split("+")[0],
                                                                    '%Y-%m-%d %H:%M:%S.%f')
                except:
                    last_scan_datetime = datetime.datetime.strptime(str(accessory.last_scan).split("+")[0],
                                                                    '%Y-%m-%d %H:%M:%S')
                current_data_time = datetime.datetime.now()
                difference = current_data_time - last_scan_datetime
                time_seconds = difference.total_seconds()

                difference = int(difference.total_seconds() / 60)
                toy_settings = ToySetting.objects.filter(toy=accessory.toy).first()

                intervals = difference / toy_settings.decreasing_time_interval
                print("intervals", intervals)
                if intervals == 1.0:
                    health_bar = accessory.health_status - toy_settings.decreasing_percentage
                    health(health_bar, accessory, time_seconds)
                elif intervals > 1.0:
                    health_bar = accessory.health_status - toy_settings.decreasing_percentage * intervals
                    health(health_bar, accessory, time_seconds)


def health(health_bar, accessory, time_seconds):

    if health_bar >= 0:
        accessory.health_status = health_bar
        accessory.last_scan = django.utils.timezone.now()
        accessory.save()
    else:
        accessory.health_status = 0
        accessory.save()
