from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from train_station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Trip,
    Order,
    Ticket,
    Crew,
)

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station_a = Station.objects.create(
            name="Station A", latitude=1, longitude=1
        )
        cls.station_b = Station.objects.create(
            name="Station B", latitude=2, longitude=2
        )
        cls.train_type = TrainType.objects.create(name="Test Train Type")
        cls.train = Train.objects.create(
            name="Express Train",
            cargo_num=1,
            places_in_cargo=1,
            train_type=cls.train_type,
        )
        cls.route = Route.objects.create(
            source=cls.station_a, destination=cls.station_b, distance=100
        )


class TrainTypeModelTest(TestCase):
    def test_train_type_str(self):
        train_type = TrainType.objects.create(name="Test Type")
        self.assertEqual(str(train_type), "Test Type")


class TrainModelTest(BaseTestCase):
    def test_train_str(self):
        self.assertEqual(
            str(self.train), f"{self.train.name} ({self.train.train_type})"
        )


class StationModelTest(TestCase):
    def test_station_str(self):
        station = Station.objects.create(
            name="Test Station", latitude=10, longitude=20
        )
        self.assertEqual(
            str(station),
            f"{station.name} ({station.latitude}, {station.longitude})",
        )


class RouteModelTest(BaseTestCase):
    def test_route_str(self):
        self.assertEqual(
            str(self.route), f"{self.station_a.name} to {self.station_b.name}"
        )

    def test_save_route(self):
        reverse_route = Route.objects.filter(
            source=self.station_b, destination=self.station_a
        )
        self.assertEqual(Route.objects.count(), 2)
        self.assertEqual(reverse_route.count(), 1)


class TripModelTest(BaseTestCase):
    def test_trip_str(self):
        trip = Trip.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        self.assertEqual(str(trip), f"{self.route} ({self.train})")


class CrewModelTest(TestCase):
    def test_crew_str(self):
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.assertEqual(str(crew), "John Doe")

    def test_crew_full_name(self):
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.assertEqual(crew.full_name, "John Doe")


class TicketModelTest(BaseTestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@example.com")
        self.trip = Trip.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.user)

    def test_ticket_str(self):
        ticket = Ticket.objects.create(
            cargo=10, seat=5, trip=self.trip, order=self.order
        )
        self.assertEqual(
            str(ticket),
            f"{self.trip} (cargo: {ticket.cargo}, seat: {ticket.seat})",
        )
