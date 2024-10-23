from rest_framework import serializers

from train_station.models import (
    Crew,
    Train,
    Station,
    Route,
    Trip,
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
    source = StationSerializer()
    destination = StationSerializer()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(
        source="source.name", read_only=True
    )
    destination = serializers.CharField(
        source="destination.name", read_only=True
    )


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class TripListSerializer(TripSerializer):
    route = RouteListSerializer(read_only=True)
    train = serializers.CharField(
        source="train.name", read_only=True
    )


class CrewSerializer(serializers.ModelSerializer):
    trips = TripListSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "trips", "full_name",)
