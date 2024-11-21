from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from train_station.models import TrainType, Train, Station, Route, Trip


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
        response = self.client.post(
            STATION_LIST_URL,
            {"name": "New Station", "latitude": 10.0, "longitude": 20.0},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_order(self):
        response = self.client.post(
            ORDER_LIST_URL,
            {"tickets": [{"seat": 1, "cargo": 1, "trip": sample_trip().id}]},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


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
        response = self.client.post(
            STATION_LIST_URL,
            {"name": "Admin Station", "latitude": 10.0, "longitude": 20.0},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_access_route_list(self):
        response = self.client.get(ROUTE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_route(self):
        source = sample_station(name="Source", latitude=50.0, longitude=30.0)
        destination = sample_station(
            name="Destination", latitude=60.0, longitude=40.0
        )
        response = self.client.post(
            ROUTE_LIST_URL,
            {
                "source": source.id,
                "destination": destination.id,
                "distance": 15,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_access_trip_list(self):
        response = self.client.get(TRIP_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_trip(self):
        route = sample_route()
        train = sample_train()
        response = self.client.post(
            TRIP_LIST_URL,
            {
                "route": route.id,
                "train": train.id,
                "departure_time": "2024-11-19 22:00:00",
                "arrival_time": "2024-11-20 22:00:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
