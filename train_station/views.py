from rest_framework import viewsets

from train_station.models import (
    Train,
    Station,
    Route,
)
from train_station.serializers import (
    TrainSerializer,
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type").all()
    serializer_class = TrainSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer
