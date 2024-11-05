from django.db.models import F, Count
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
    RouteDetailSerializer,
    TripSerializer,
    TripListSerializer,
    CrewSerializer,
    OrderSerializer,
    OrderListSerializer,
    TripDetailSerializer,
    CrewListSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related(
        "trips__route__source",
        "trips__route__destination",
        "trips__train__train_type",
    )
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related(
        "route__source",
        "route__destination",
        "train__train_type",
    ).annotate(
        tickets_available=(
            F("train__cargo_num") * F("train__places_in_cargo")
            - Count("tickets")
        )
    )
    serializer_class = TripSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer

        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets")
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
