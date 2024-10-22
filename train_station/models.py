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
        TrainType,
        on_delete=models.CASCADE,
        related_name="train_types"
    )

    def __str__(self):
        return f"{self.name} ({self.train_type})"
