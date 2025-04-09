from django.urls import include, path
from rest_framework import routers

from cosmoshow.views import ShowThemeViewSet, AstronomyShowViewSet, PlanetariumDomeViewSet, ShowSessionViewSet, \
    ReservationViewSet

router = routers.DefaultRouter()
router.register("show-themes", ShowThemeViewSet, basename="show-theme")
router.register("astronomy-shows", AstronomyShowViewSet, basename="astronomy-show")
router.register("planetarium-domes", PlanetariumDomeViewSet, basename="planetarium-dome")
router.register("show-sessions", ShowSessionViewSet, basename="show-session")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = [path('', include(router.urls))]

app_name = "cosmoshow"
