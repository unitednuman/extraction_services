from django.urls import path
from .views import HouseAuctionView, HouseAuctionViewDetails

urlpatterns = [
    path('auction/', HouseAuctionView.as_view()),
    path("auction/<int:pk>/", HouseAuctionViewDetails.as_view()),

]
