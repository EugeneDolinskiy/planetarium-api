from rest_framework import serializers

from cosmoshow.models import ShowTheme, AstronomyShow


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = (
            "id",
            "name"
        )


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        models = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "themes"
        )
