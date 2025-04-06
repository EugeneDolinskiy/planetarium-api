from rest_framework import serializers

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Reservation, Ticket


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = (
            "id",
            "name"
        )


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "themes"
        )


class AstronomyShowListSerializer(AstronomyShowSerializer):
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "themes"
        )


class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row"
        )


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time"
        )


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title"
    )
    planetarium_dome = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowRetrieveSerializer()
    planetarium_dome = PlanetariumDomeSerializer()


class TickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "show_session"
        )


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TickSerializer(many=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "created_at",
            "user",
            "tickets"
        )

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation
