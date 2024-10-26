from rest_framework import serializers

from train_station.models import (
    Crew,
    Train,
    Station,
    Route,
    Trip,
    Ticket,
    Order,
)


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.CharField(
        source="train_type.name", read_only=True
    )

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(
        source="destination.name", read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TripSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination"),
    )
    train = serializers.PrimaryKeyRelatedField(
        queryset=Train.objects.select_related("train_type"),
    )
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class TripListSerializer(TripSerializer):
    route = serializers.StringRelatedField(read_only=True)
    train = serializers.StringRelatedField(read_only=True)


class TripDetailSerializer(TripSerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    trips = TripListSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "trips",
            "full_name",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
