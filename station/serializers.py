from rest_framework import serializers

from station.models import Station, TrainType, Route, Train, Crew, Journey


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "capacity", "train_type")


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class JourneySerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False, read_only=True)
    train = TrainSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")
