from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from cosmoshow.models import ShowTheme, AstronomyShow, ShowSession, Reservation, PlanetariumDome
from cosmoshow.serializers import ShowThemeSerializer, AstronomyShowSerializer, AstronomyShowRetrieveSerializer, \
    ShowSessionListSerializer, ShowSessionRetrieveSerializer, ShowSessionSerializer, ReservationSerializer, \
    ReservationListSerializer, PlanetariumDomeSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    serializer_class = ShowThemeSerializer

    def get_queryset(self):
        queryset = ShowTheme.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    serializer_class = PlanetariumDomeSerializer

    def get_queryset(self):
        queryset = PlanetariumDome.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowSerializer
        elif self.action == "retrieve":
            return AstronomyShowRetrieveSerializer

        return AstronomyShowSerializer

    def get_queryset(self):
        queryset = self.queryset

        themes = self.request.query_params.get("themes")

        if themes:
            themes = self._params_to_ints(themes)
            queryset = queryset.filter(themes__id__in=themes)

        queryset = queryset.distinct()

        if self.action in ["list", "retrieve"]:
            return queryset.prefetch_related("themes")

        return queryset


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer

        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            tickets_available = (
                F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                - Count("tickets_taken")
            )

            return (
                queryset
                .select_related()
                .annotate(tickets_available=tickets_available)
                .order_by("id")
            )

        if self.action == "retrieve":
            return queryset.select_related()

        return queryset


class ReservationSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationSetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__show_session__astronomy_show",
                "tickets__show_session__planetarium_dome"
            )

        if self.action == "retrieve":
            return queryset.prefetch_related("tickets")

        return queryset.select_related()

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = ReservationListSerializer

        return serializer
