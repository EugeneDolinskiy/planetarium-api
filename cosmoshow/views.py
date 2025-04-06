from rest_framework import viewsets

from cosmoshow.models import ShowTheme, AstronomyShow
from cosmoshow.serializers import ShowThemeSerializer, AstronomyShowSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer
