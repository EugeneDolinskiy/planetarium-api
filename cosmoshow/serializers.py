from rest_framework import serializers

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome


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
