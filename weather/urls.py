from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.index, name="index"),
    path("autocomplete/", views.city_autocomplete, name="city_autocomplete"),
    path("api/city-stats/", api.city_search_stats, name="city_search_stats"),
]
