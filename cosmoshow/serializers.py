from django.db import transaction
from rest_framework import serializers

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Ticket, Reservation


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ["id", "name"]


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ["id", "title", "description", "themes"]


class AstronomyShowListSerializer(serializers.ModelSerializer):
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )


class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "capacity"]


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = [
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time"
        ]


class ShowSessionListSerializer(serializers.ModelSerializer):
    show_info = serializers.CharField(
        source="astronomy_show.title",
        read_only=True
    )
    dome_name = serializers.CharField(
        source="planetarium_dome.name",
        read_only=True
    )
    dome_num_seats = serializers.IntegerField(
        source="planetarium_dome.capacity",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = [
            "id",
            "show_info",
            "dome_name",
            "dome_num_seats",
            "tickets_available",
            "show_time"
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "show_session"
        ]

    def validate(self, attrs):
        show_session = attrs["show_session"]
        seat = attrs["seat"]
        row = attrs["row"]

        dome = show_session.planetarium_dome
        num_seats = dome.seats_in_row
        num_rows = dome.rows

        Ticket.validate_seat(seat, num_seats, serializers.ValidationError)
        Ticket.validate_row(row, num_rows, serializers.ValidationError)

        return attrs


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowRetrieveSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets"
    )

    class Meta:
        model = ShowSession
        fields = [
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "taken_seats"
        ]


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
