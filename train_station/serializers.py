from django.db import transaction
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
    train_type = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, data):
        if data["source"] == data["destination"]:
            raise serializers.ValidationError(
                "Source and destination stations cannot be the same."
            )

        if data["distance"] <= 0:
            raise serializers.ValidationError(
                "Distance must be a positive value."
            )

        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(
        slug_field="name", read_only=True
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
    trips = TripSerializer(many=True)

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "trips",
            "full_name",
        )


class CrewListSerializer(CrewSerializer):
    trips = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "full_name", "trips")


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

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
