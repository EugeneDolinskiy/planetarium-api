from rest_framework import viewsets

from cosmoshow.models import ShowTheme
from cosmoshow.serializers import ShowThemeSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
