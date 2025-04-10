from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cosmoshow.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes")


class AstronomyShowListSerializer(AstronomyShowBaseSerializer):
    themes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")


class AstronomyShowRetrieveSerializer(AstronomyShowBaseSerializer):
    themes = ShowThemeSerializer(many=True)


class PlanetariumDomeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PlanetariumDomeListSerializer(PlanetariumDomeBaseSerializer):
    class Meta(PlanetariumDomeBaseSerializer.Meta):
        fields = ("name", "capacity")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.CharField(
        source="astronomy_show.title", read_only=True
    )
    dome_name = serializers.CharField(source="planetarium_dome.name", read_only=True)
    dome_capacity = serializers.IntegerField(
        source="planetarium_dome.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)
    show_time = serializers.SerializerMethodField()

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "dome_name",
            "dome_capacity",
            "tickets_available",
            "show_time",
        )

    def get_show_time(self, obj):
        if obj.show_time:
            return obj.show_time.strftime("%Y-%m-%d, %H:%M")
        return None


class TicketSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowListSerializer(read_only=True)
    planetarium_dome = PlanetariumDomeListSerializer(read_only=True)
    tickets_taken = TicketSeatSerializer(many=True, read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "tickets_taken",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")

    def validate(self, attrs):
        show_session = attrs.get("show_session")
        row = attrs.get("row")
        seat = attrs.get("seat")

        if show_session:

            planetarium_dome = show_session.planetarium_dome
            num_rows = planetarium_dome.rows
            num_seats = planetarium_dome.seats_in_row

            Ticket.validate_row(row, num_rows, serializers.ValidationError)
            Ticket.validate_seat(seat, num_seats, serializers.ValidationError)

        return attrs


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)

            for ticket_data in tickets_data:
                show_session = ticket_data.get("show_session")
                row = ticket_data.get("row")
                seat = ticket_data.get("seat")

                existing_ticket = Ticket.objects.filter(
                    show_session=show_session, row=row, seat=seat
                ).exists()

                if existing_ticket:
                    raise ValidationError(
                        f"Seat {row}-{seat} is already taken for this show session."
                    )

                Ticket.objects.create(reservation=reservation, **ticket_data)

            return reservation


class ReservationListSerializer(serializers.ModelSerializer):
    show_title = serializers.SerializerMethodField()
    tickets_count = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "show_title", "session_date", "tickets_count")

    def get_first_ticket(self, obj):
        return (
            obj.prefetched_tickets[0]
            if hasattr(obj, "prefetched_tickets") and obj.prefetched_tickets
            else None
        )

    def get_tickets_count(self, obj):
        return len(obj.prefetched_tickets) if hasattr(obj, "prefetched_tickets") else 0

    def get_show_title(self, obj):
        ticket = self.get_first_ticket(obj)
        if ticket and ticket.show_session and ticket.show_session.astronomy_show:
            return ticket.show_session.astronomy_show.title

    def get_session_date(self, obj):
        ticket = self.get_first_ticket(obj)
        if ticket and ticket.show_session and ticket.show_session.show_time:
            return ticket.show_session.show_time.strftime("%Y-%m-%d, %H:%M")

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d, %H:%M")


class ReservationRetrieveSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")
