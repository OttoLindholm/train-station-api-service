from django.urls import path, include
from rest_framework import routers

from train_station.views import (
    StationViewSet,
    TrainViewSet,
    TripViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("trips", TripViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train-station"
