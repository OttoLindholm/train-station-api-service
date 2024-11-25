from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from train_station.models import TrainType, Train, Station, Route, Trip, Order
from train_station.serializers import TripListSerializer

CREW_LIST_URL = reverse("train-station:crew-list")
TRAIN_LIST_URL = reverse("train-station:train-list")
STATION_LIST_URL = reverse("train-station:station-list")
ROUTE_LIST_URL = reverse("train-station:route-list")
TRIP_LIST_URL = reverse("train-station:trip-list")
ORDER_LIST_URL = reverse("train-station:order-list")


def sample_train(**params):
    train_type = TrainType.objects.create(name="Sample type")
    defaults = {
        "name": "Sample train",
        "cargo_num": 1,
        "places_in_cargo": 1,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 1.0,
        "longitude": 1.0,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_route(**params):
    source = sample_station(name="Sample source")
    destination = sample_station(name="Sample destination")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 10.5,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_trip(**params):
    route = sample_route()
    train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": make_aware(datetime(2024, 11, 19, 22, 0, 0)),
        "arrival_time": make_aware(datetime(2024, 11, 20, 22, 0, 0)),
    }
    defaults.update(params)
    return Trip.objects.create(**defaults)


def remove_tickets_available(data):
    return {
        key: value for key, value in data.items() if key != "tickets_available"
    }


def detail_url(view_name, pk):
    return reverse(f"train-station:{view_name}-detail", kwargs={"pk": pk})


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_cannot_access_crew_list(self):
        response = self.client.get(CREW_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_access_station_list(self):
        response = self.client.get(STATION_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_access_route_list(self):
        response = self.client.get(ROUTE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_access_trip_list(self):
        response = self.client.get(TRIP_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@mail.test", password="password"
        )
        self.client.force_authenticate(user=self.user)

    def test_can_access_station_list(self):
        response = self.client.get(STATION_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_access_route_list(self):
        response = self.client.get(ROUTE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_access_trip_list(self):
        response = self.client.get(TRIP_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_create_station(self):
        data = {"name": "New Station", "latitude": 10.0, "longitude": 20.0}
        response = self.client.post(
            STATION_LIST_URL,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_trip_by_train(self):
        trip1 = sample_trip(train=sample_train(name="Train 1"))
        trip2 = sample_trip(train=sample_train(name="Train 2"))
        trip3 = sample_trip(train=sample_train(name="Else"))

        res = self.client.get(TRIP_LIST_URL, {"train": "train"})

        serializer1 = TripListSerializer(trip1)
        serializer2 = TripListSerializer(trip2)
        serializer3 = TripListSerializer(trip3)
        res_data = [remove_tickets_available(item) for item in res.data]

        self.assertIn(serializer1.data, res_data)
        self.assertIn(serializer2.data, res_data)
        self.assertNotIn(serializer3.data, res_data)

    def test_filter_trip_by_source_or_destination(self):
        trip1 = sample_trip(
            route=sample_route(
                source=sample_station(name="Station 1"),
                destination=sample_station(name="Station 1"),
            )
        )
        trip2 = sample_trip(
            route=sample_route(
                source=sample_station(name="Station 2"),
                destination=sample_station(name="Station 2"),
            )
        )
        trip3 = sample_trip(
            route=sample_route(
                source=sample_station(name="Else"),
                destination=sample_station(name="Else"),
            )
        )

        serializer1 = TripListSerializer(trip1)
        serializer2 = TripListSerializer(trip2)
        serializer3 = TripListSerializer(trip3)

        res = self.client.get(TRIP_LIST_URL, {"source": "station"})
        res_data = [remove_tickets_available(item) for item in res.data]

        self.assertIn(serializer1.data, res_data)
        self.assertIn(serializer2.data, res_data)
        self.assertNotIn(serializer3.data, res_data)

        res = self.client.get(TRIP_LIST_URL, {"destination": "station"})
        res_data = [remove_tickets_available(item) for item in res.data]

        self.assertIn(serializer1.data, res_data)
        self.assertIn(serializer2.data, res_data)
        self.assertNotIn(serializer3.data, res_data)

    def test_filter_trip_by_date(self):
        trip1 = sample_trip(
            departure_time=make_aware(datetime(2024, 11, 25, 8, 0)),
            arrival_time=make_aware(datetime(2024, 11, 26, 8, 0)),
        )
        trip2 = sample_trip(
            departure_time=make_aware(datetime(2024, 11, 25, 10, 0)),
            arrival_time=make_aware(datetime(2024, 11, 26, 10, 0)),
        )

        trip3 = sample_trip(
            departure_time=make_aware(datetime(2024, 11, 26, 10, 0)),
            arrival_time=make_aware(datetime(2024, 11, 27, 10, 0)),
        )

        serializer1 = TripListSerializer(trip1)
        serializer2 = TripListSerializer(trip2)
        serializer3 = TripListSerializer(trip3)

        res = self.client.get(TRIP_LIST_URL, {"departure": "2024-11-25"})
        res_data = [remove_tickets_available(item) for item in res.data]

        self.assertIn(serializer1.data, res_data)
        self.assertIn(serializer2.data, res_data)
        self.assertNotIn(serializer3.data, res_data)

        res = self.client.get(TRIP_LIST_URL, {"arrival": "2024-11-26"})
        res_data = [remove_tickets_available(item) for item in res.data]

        self.assertIn(serializer1.data, res_data)
        self.assertIn(serializer2.data, res_data)
        self.assertNotIn(serializer3.data, res_data)

    def test_can_create_order(self):
        data = {"tickets": [{"seat": 1, "cargo": 1, "trip": sample_trip().id}]}
        response = self.client.post(
            ORDER_LIST_URL,
            data=data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Order.objects.all().count(), 1)


class AdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@mail.test", password="admin"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_can_access_station_list(self):
        response = self.client.get(STATION_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_station(self):
        data = {"name": "Admin Station", "latitude": 10.0, "longitude": 20.0}
        response = self.client.post(
            STATION_LIST_URL,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Station.objects.all().count(), 1)

    def test_can_access_route_list(self):
        response = self.client.get(ROUTE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_route(self):
        source = sample_station(name="Source", latitude=50.0, longitude=30.0)
        destination = sample_station(
            name="Destination", latitude=60.0, longitude=40.0
        )
        data = {
            "source": source.id,
            "destination": destination.id,
            "distance": 15,
        }
        response = self.client.post(
            ROUTE_LIST_URL,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.all().count(), 2)

    def test_can_access_trip_list(self):
        response = self.client.get(TRIP_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_trip(self):
        route = sample_route()
        train = sample_train()
        data = {
            "route": route.id,
            "train": train.id,
            "departure_time": "2024-11-19 22:00:00",
            "arrival_time": "2024-11-20 22:00:00",
        }
        response = self.client.post(
            TRIP_LIST_URL,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trip.objects.all().count(), 1)
