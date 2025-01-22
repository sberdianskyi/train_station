from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from station.models import Station, Route, TrainType, Train, Crew, Journey, Order
from station.serializers import (
    StationSerializer,
    RouteSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    JourneySerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainListSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer
)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all().select_related()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(ModelViewSet):
    queryset = Train.objects.all().select_related()
    serializer_class = TrainSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = queryset

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(
    ModelViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = (queryset.select_related(
                "route__source", "route__destination", "train__train_type"
            ).prefetch_related("train__train_type"))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route", "tickets__journey__train"
    ).all()
    serializer_class = OrderSerializer
