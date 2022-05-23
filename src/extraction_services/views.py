from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from rest_framework import generics, status, pagination
from rest_framework import response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# from utils.permissions import IsAppAdmin, IsNonAdminUser
from rest_framework import filters
from django.db.models import Q
from .models import HouseAuction
from .serializers import HouseAuctionSerializer
from django.db import connection
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
import datetime
from django.utils.timezone import now
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


# Create your views here.
class HouseAuctionView(generics.GenericAPIView):
    queryset = HouseAuction.objects.all()
    serializer_class = HouseAuctionSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('search', openapi.IN_QUERY,
                          description='Search name',
                          type=openapi.TYPE_STRING, required=False, default=None),
    ])
    def get(self, request, *args, **kwargs):
        # search = request.GET.get('search', '')

        data = self.queryset.all()
        paginated_response = self.paginate_queryset(data)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)

    def post(self, request, *args, **kwargs):
        serialized = self.get_serializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return response.Response(serialized.data, status=status.HTTP_201_CREATED)
        return response.Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class HouseAuctionViewDetails(generics.GenericAPIView):
    queryset = HouseAuction.objects.all()
    serializer_class = HouseAuctionSerializer

    def get(self, *args, **kwargs):
        if kwargs.get('pk'):
            toy_data = self.queryset.filter(pk=kwargs.get('pk'))
            paginated_response = self.paginate_queryset(toy_data)
            serialized = self.get_serializer(paginated_response, many=True)
            return self.get_paginated_response(serialized.data)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            toy_data = self.queryset.get(pk=kwargs.get('pk'))
            serialized = self.get_serializer(toy_data, data=request.data, partial=True)
            if serialized.is_valid():
                serialized.save()
                data = {
                    'status': status.HTTP_200_OK,
                    'message': "Update Successful"
                }
                return response.Response(data)
            return response.Response(serialized.errors)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            toy_data = self.queryset.get(pk=kwargs.get('pk'))
            toy_data.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
