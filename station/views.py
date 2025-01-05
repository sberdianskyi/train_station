from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from station.models import Station, Route, TrainType, Train, Crew, Journey
from station.serializers import StationSerializer, RouteSerializer, TrainTypeSerializer, TrainSerializer, \
    CrewSerializer, JourneySerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
