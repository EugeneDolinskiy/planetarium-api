from django.db.models import F, Count, Prefetch, Q
from django.utils.dateparse import parse_date
from rest_framework import viewsets

from cosmoshow.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)
from cosmoshow.serializers import (
    ShowThemeSerializer,
    AstronomyShowBaseSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
    PlanetariumDomeBaseSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ReservationRetrieveSerializer,
)


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
        title = self.request.query_params.get("title")

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("themes")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeBaseSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


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
        title = self.request.query_params.get("title")
        date = self.request.query_params.get("date")

        if title:
            queryset = queryset.filter(astronomy_show__title__icontains=title)

        if date:
            parsed_date = parse_date(date)
            if parsed_date:
                queryset = queryset.filter(show_time__date=date)

        return queryset.distinct()


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
        title = self.request.query_params.get("title")
        date = self.request.query_params.get("date")

        first_ticket_prefetch = Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "show_session__astronomy_show", "show_session__planetarium_dome"
            ).order_by("id"),
            to_attr="prefetched_tickets",
        )

        queryset = Reservation.objects.filter(user=self.request.user).prefetch_related(
            first_ticket_prefetch
        )

        if title or date:
            filters = Q()

            if title:
                filters &= Q(
                    tickets__show_session__astronomy_show__title__icontains=title
                )

            if date:
                parsed_date = parse_date(date)
                if parsed_date:
                    filters &= Q(tickets__show_session__show_time__date=parsed_date)

            queryset = queryset.filter(filters).distinct()

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
