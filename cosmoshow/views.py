from django.db.models import F, Count
from rest_framework import viewsets

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Reservation
from cosmoshow.serializers import ShowThemeSerializer, AstronomyShowBaseSerializer, AstronomyShowListSerializer, \
    AstronomyShowRetrieveSerializer, PlanetariumDomeBaseSerializer, ShowSessionListSerializer, \
    ShowSessionRetrieveSerializer, ShowSessionSerializer, ReservationSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        elif self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return AstronomyShowBaseSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("themes")


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeBaseSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = (
        ShowSession.objects.all()
        .select_related("astronomy_show", "planetarium_dome")
        .annotate(
            tickets_available=(
                F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                - Count("tickets_taken")
            )
        )
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("astronomy_show", "planetarium_dome")


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__show_session")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "retrieve":
            return ReservationRetrieveSerializer
        return ReservationSerializer
