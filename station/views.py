from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from station.models import Station
from station.serializers import StationSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
