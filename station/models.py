import os
import uuid
from math import radians, sin, cos, atan2, sqrt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


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

    @property
    def route_name(self):
        return f"{self.source.name} - {self.destination.name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/crews/", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=image_file_path)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return (f"{self.route.source.name} - {self.route.destination.name}: "
                f"departure at {self.departure_time} "
                )


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(seat: int, cargo: int, train, error_to_raise):
        if seat < 1 or seat > train.places_in_cargo:
            raise error_to_raise(
                f"Seat number {seat} is not valid. Cargo capacity: {train.places_in_cargo}")

        if cargo < 0 or cargo > train.cargo_num:
            raise error_to_raise(
                f"Cargo value {cargo} exceeds the train's capacity of {train.cargo_num}")

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.cargo,
            self.journey.train,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        return super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.journey}: cargo {self.cargo}, seat {self.seat}"

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]
