from rest_framework import viewsets

from train_station.models import (
    Train, Station,
)
from train_station.serializers import (
    TrainSerializer, StationSerializer,
)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
