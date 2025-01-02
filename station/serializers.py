from rest_framework import serializers

from station.models import Station


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")
        read_only_fields = ("id",)
