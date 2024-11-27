from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from train_station.permissions import IsAdminOrIfAuthenticatedReadOnly
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


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crew.objects.prefetch_related(
        "trips__route__source",
        "trips__route__destination",
        "trips__train__train_type",
    )
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        train = self.request.query_params.get("train")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_date = self.request.query_params.get("departure")
        arrival_date = self.request.query_params.get("arrival")

        queryset = self.queryset

        if train:
            queryset = queryset.filter(train__name__icontains=train)

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(
                route__destination__name__icontains=destination
            )

        if departure_date:
            date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if arrival_date:
            date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=date)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer

        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train",
                type=OpenApiTypes.STR,
                description="Filter by Train name (ex. ?train=regional)",
            ),
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source of Trip (ex. ?source=Lviv)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination of Trip (ex. ?source=Dnipro)",
            ),
            OpenApiParameter(
                "departure",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure date of Trip (ex. ?date=2024-11-25)"
                ),
            ),
            OpenApiParameter(
                "arrival",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by arrival date of Trip (ex. ?date=2024-11-26)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__train__train_type",
        "tickets__trip__route__source",
        "tickets__trip__route__destination",
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
