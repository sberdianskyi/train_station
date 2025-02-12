from datetime import datetime
from django.db.models import F, Count

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from station.models import Station, Route, TrainType, Train, Crew, Journey
from station.serializers import JourneyListSerializer


JOURNEY_URL = reverse("station:journey-list")


def test_station(**params) -> Station:
    default_station = {
        "name": "Kharkiv",
        "latitude": 49.98956,
        "longitude": 36.2043,
    }

    default_station.update(params)

    return Station.objects.create(**default_station)


def test_route(**params) -> Route:
    source = test_station()
    destination = test_station(
        name="Kyiv",
        latitude=50.44056,
        longitude=30.48944
    )
    default_route = {
        "source": source,
        "destination": destination,
    }
    default_route.update(params)
    return Route.objects.create(**default_route)


def test_train_type(**params) -> TrainType:
    default_train_type = {"name": "Normal: speed up to 120 km/h"}
    default_train_type.update(params)
    return TrainType.objects.create(**default_train_type)


def test_train(**params) -> Train:
    train_type = test_train_type()
    default_train = {
        "name": "Hyundai Rotem HRCS2",
        "cargo_num": 9,
        "places_in_cargo": 69,
        "train_type": train_type,
    }
    default_train.update(params)
    return Train.objects.create(**default_train)


def test_crew(**params) -> Crew:
    default_crew = {"first_name": "Harry", "last_name": "Potter"}
    default_crew.update(params)
    return Crew.objects.create(**default_crew)


def test_journey(**params) -> Journey:
    route = test_route()
    train = test_train()
    default_journey = {
        "route": route,
        "train": train,
        "departure_time": "2025-01-05 15:00:00",
        "arrival_time": "2025-01-05 22:00:00",
    }
    default_journey.update(params)
    return Journey.objects.create(**default_journey)


def journey_detail_url(journey_id: int):
    return reverse("station:journey-detail", args=(journey_id,))


def normalize_datetime_format(data):
    for journey in data:
        journey["departure_time"] = datetime.strptime(
            journey["departure_time"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d %H:%M:%S")
        journey["arrival_time"] = datetime.strptime(
            journey["arrival_time"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d %H:%M:%S")
    return data


class UnauthenticatedJourneyViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_journey_list(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_journey_detail(self):
        movie = test_journey()
        url = journey_detail_url(movie.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="sample@test.com", password="test_password"
        )
        self.client.force_authenticate(self.user)

    @staticmethod
    def serializer_data_with_tickets_available(journeys):
        queryset = (
            Journey.objects.filter(id__in=[j.id for j in journeys])
            .annotate(
                tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count("tickets")
                )
            )
        )
        return JourneyListSerializer(queryset, many=True).data

    def test_journey_list(self):
        journey_with_crew = test_journey()
        crew = test_crew()
        crew_1 = test_crew(first_name="Hermione", last_name="Granger")
        journey_with_crew.crew.add(crew, crew_1)

        res = self.client.get(JOURNEY_URL)
        expected_data = (
            self.serializer_data_with_tickets_available(
                [journey_with_crew]
            )
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    def test_filter_journey_by_route_id(self):
        source = test_station(
            name="Kremenchuk",
            latitude=49.06794,
            longitude=33.42786
        )
        destination = test_station(
            name="Donetsk", latitude=48.04401, longitude=37.74616
        )
        route = test_route(source=source, destination=destination)
        journey = test_journey(route=route)
        journey_1 = test_journey()

        res = self.client.get(JOURNEY_URL, {"routes": route.id})
        expected_data = self.serializer_data_with_tickets_available(
            [journey, journey_1]
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    #

    def test_filter_journey_by_date(self):
        journey = test_journey(departure_time="2025-01-05 15:00:00")

        res = self.client.get(JOURNEY_URL, {"date": "2025-01-05"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = self.serializer_data_with_tickets_available([journey])
        self.assertEqual(res.data, expected_data)

    def test_filter_journey_by_source_name(self):
        journey = test_journey()

        res = self.client.get(JOURNEY_URL, {"source_name": "Kharkiv"})
        expected_data = self.serializer_data_with_tickets_available([journey])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    def test_filter_journey_by_destination_name(self):
        destination = test_station(
            name="Donetsk", latitude=48.04401, longitude=37.74616
        )
        route = test_route(destination=destination)
        journey = test_journey(route=route)

        res = self.client.get(JOURNEY_URL, {"dest_name": "Donetsk"})
        expected_data = self.serializer_data_with_tickets_available([journey])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)


class AdminJourneyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    #
    def test_create_journey(self):
        route = test_route()
        train = test_train()
        crew = test_crew()
        crew_1 = test_crew(first_name="Sheldon", last_name="Cooper")
        payload = {
            "route": [route.id],
            "train": [train.id],
            "departure_time": "2025-01-05 15:00:00",
            "arrival_time": "2025-01-05 22:00:00",
            "crew": [crew.id, crew_1.id],
        }
        res = self.client.post(JOURNEY_URL, payload)
        journey = Journey.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(journey.route, route)
        self.assertEqual(journey.train, train)
        self.assertEqual(list(journey.crew.all()), [crew, crew_1])
