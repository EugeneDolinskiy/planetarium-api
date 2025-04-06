from django.contrib import admin

from cosmoshow.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession

admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(PlanetariumDome)
admin.site.register(ShowSession)
