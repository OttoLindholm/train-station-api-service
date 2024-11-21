from django.db import models

from train_station_service import settings


class TrainType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=50)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="train_types"
    )

    def __str__(self):
        return f"{self.name} ({self.train_type})"


class Station(models.Model):
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes_as_source"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes_as_destination"
    )
    distance = models.IntegerField()

    class Meta:
        ordering = ["source", "destination"]

    def __str__(self):
        return f"{self.source.name} to {self.destination.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        Route.objects.get_or_create(
            source=self.destination,
            destination=self.source,
            defaults={"distance": self.distance},
        )


class Trip(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="trips"
    )
    train = models.ForeignKey(
        Train, on_delete=models.CASCADE, related_name="trips"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} ({self.train})"


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    trips = models.ManyToManyField(Trip)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return self.__str__()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return f"{self.trip} (cargo: {self.cargo}, seat: {self.seat})"

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ["cargo", "seat"]