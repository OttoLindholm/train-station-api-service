from django.test import TestCase
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from train_station.models import Station, Route, Trip, TrainType, Train
from train_station.serializers import RouteSerializer, OrderSerializer
from user.models import User


class RouteSerializerValidationTestCase(TestCase):

    def setUp(self):
        self.station_a = Station.objects.create(
            name="Station A", latitude=10.0, longitude=20.0
        )
        self.station_b = Station.objects.create(
            name="Station B", latitude=15.0, longitude=25.0
        )

    def test_valid_route_data(self):
        valid_data = {
            "source": self.station_a.id,
            "destination": self.station_b.id,
            "distance": 100,
        }
        serializer = RouteSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_same_source_and_destination(self):
        invalid_data = {
            "source": self.station_a.id,
            "destination": self.station_a.id,
            "distance": 100,
        }
        serializer = RouteSerializer(data=invalid_data)

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            "Source and destination stations cannot be the same",
            str(context.exception),
        )

    def test_invalid_negative_distance(self):
        invalid_data = {
            "source": self.station_a.id,
            "destination": self.station_b.id,
            "distance": -50,
        }
        serializer = RouteSerializer(data=invalid_data)

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            "Distance must be a positive value", str(context.exception)
        )


class OrderSerializerCreateTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser", password="12345"
        )
        station_a = Station.objects.create(
            name="Station A", latitude=10.0, longitude=20.0
        )
        station_b = Station.objects.create(
            name="Station B", latitude=15.0, longitude=25.0
        )
        route = Route.objects.create(
            source=station_a, destination=station_b, distance=100
        )
        train = Train.objects.create(
            name="Train A",
            cargo_num=5,
            places_in_cargo=100,
            train_type=TrainType.objects.create(name="Train Type"),
        )

        self.trip = Trip.objects.create(
            route=route,
            train=train,
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2),
        )

    def test_create_order_with_valid_tickets(self):
        ticket_data = [{"cargo": 1, "seat": 1, "trip": self.trip.id}]
        order_data = {"tickets": ticket_data}

        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        order = serializer.save(user=self.user)

        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.tickets.first().seat, 1)
        self.assertEqual(order.tickets.first().trip, self.trip)

    def test_create_order_with_invalid_tickets(self):
        invalid_ticket_data = [{"cargo": 1, "seat": 1, "trip": None}]
        order_data = {"tickets": invalid_ticket_data}

        serializer = OrderSerializer(data=order_data)
        self.assertFalse(serializer.is_valid())

        self.assertIn("trip", serializer.errors["tickets"][0])
