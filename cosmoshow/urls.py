from django.urls import include, path
from rest_framework import routers

from cosmoshow.views import ShowThemeViewSet, AstronomyShowViewSet

router = routers.DefaultRouter()
router.register("show-themes", ShowThemeViewSet)
router.register("astronomy-shows", AstronomyShowViewSet)

urlpatterns = [path('', include(router.urls))]

app_name = "cosmoshow"
