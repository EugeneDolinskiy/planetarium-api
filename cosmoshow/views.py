from rest_framework import viewsets

from cosmoshow.models import ShowTheme, AstronomyShow
from cosmoshow.serializers import ShowThemeSerializer, AstronomyShowSerializer, AstronomyShowListSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        return AstronomyShowSerializer
