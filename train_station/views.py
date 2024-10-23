from rest_framework import viewsets

from train_station.models import (
    Train,
    Station,
    Route,
    Trip,
    Crew,
    Order,
)
from train_station.serializers import (
    TrainSerializer,
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    TripSerializer,
    TripListSerializer,
    CrewSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related("trips").all()
    serializer_class = CrewSerializer


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


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related("train", "route").all()
    serializer_class = TripSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        return TripSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("tickets").all()
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer
