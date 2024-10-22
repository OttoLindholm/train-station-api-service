from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
        Station, on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name}-{self.destination.name}"
