import math
from django.db.models import Q

from rest_framework import serializers
from .models import  HouseAuction




class HouseAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAuction
        fields = '__all__'
        # fields = 'id', 'nick_name', 'points', 'level', 'nfc_token', 'update', 'points_per_minute'

    # def create(self, validated_data):
    #     toy = Toy.objects.create(**validated_data)
    #     ToySetting.objects.create(toy=toy, decreasing_percentage=1, decreasing_time_interval=1)
    #     return toy

    # def to_representation(self, instance):
    #     data = super(ToySerializer, self).to_representation(instance)
    #     data.update(self.get_detailed_data(instance))
    #     return data
    #
    # def get_detailed_data(self, instance):
    #     return {
    #         'accessory': ToyAccessoriesSerializer(instance.toy_Accessories.all().order_by('-created'), many=True).data,
    #         'toy_settings': ToySettingSerializer(instance.toy_settings.all(), many=True).data,
    #         'level': LevelSerializer(instance.level).data
    #     }



