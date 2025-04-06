from django.urls import include, path
from rest_framework import routers

from cosmoshow.views import ShowThemeViewSet

router = routers.DefaultRouter()
router.register("show-themes", ShowThemeViewSet)

urlpatterns = [path('', include(router.urls))]

app_name = "cosmoshow"
