from math import radians, sin, cos, atan2, sqrt

from django.db import models
from django.db.models import CASCADE


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name}: {self.latitude} latitude, {self.longitude} longtitude"


class Route(models.Model):
    source = models.ForeignKey(Station, related_name="route_source", on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, related_name="route_destination", on_delete=models.CASCADE)
    distance = models.IntegerField(blank=True, null=True)  # Distance can be calculated and updated

    def save(self, *args, **kwargs):
        if self.source and self.destination:
            self.distance = self.calculate_distance()
        super().save(*args, **kwargs)

    def calculate_distance(self):
        # Haversine formula to calculate the distance between two points
        R = 6371  # Radius of the Earth in kilometers
        lat1 = radians(self.source.latitude)
        lon1 = radians(self.source.longitude)
        lat2 = radians(self.destination.latitude)
        lon2 = radians(self.destination.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c  # Distance in kilometers
        return int(distance)  # Return as an integer

    def __str__(self):
        return f"{self.source.name} - {self.destination.name} (distance: {self.distance} km)"


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE)
    train = models.ForeignKey(Train, on_delete=CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return (f"{self.route.source.name} - {self.route.destination.name}: "
                f"departure at {self.departure_time} "
                f"- arrive at {self.arrival_time}; "
                f"train: {self.train}")

