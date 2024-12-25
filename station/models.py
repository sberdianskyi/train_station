from django.db import models
from django.db.models import CASCADE


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, on_delete=models.CASCADE)
    distance = models.IntegerField()


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE)
    train = models.ForeignKey(Train, on_delete=CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")
