from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("autocomplete/", views.city_autocomplete, name="city_autocomplete")
]
