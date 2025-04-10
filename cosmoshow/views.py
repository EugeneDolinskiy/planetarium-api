from django.db.models import F, Count, Prefetch
from rest_framework import viewsets

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Reservation, Ticket
from cosmoshow.serializers import ShowThemeSerializer, AstronomyShowBaseSerializer, AstronomyShowListSerializer, \
    AstronomyShowRetrieveSerializer, PlanetariumDomeBaseSerializer, ShowSessionListSerializer, \
    ShowSessionRetrieveSerializer, ShowSessionSerializer, ReservationSerializer, ReservationListSerializer, \
    ReservationRetrieveSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        queryset = queryset.distinct()

        return queryset


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


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "retrieve":
            return ReservationRetrieveSerializer
        return serializer

    def get_queryset(self):
        first_ticket_prefetch = Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "show_session__astronomy_show",
                "show_session__planetarium_dome"
            ).order_by("id"), to_attr="prefetched_tickets")
        return (
            Reservation.objects
            .filter(user=self.request.user)
            .prefetch_related(first_ticket_prefetch)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
