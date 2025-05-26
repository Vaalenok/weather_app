from django.http import JsonResponse
from django.shortcuts import render
import json
import requests
import uuid

from .models import SearchHistory


def index(request):
    city = request.GET.get("city")
    cookie_id = request.COOKIES.get("user_id")

    if not cookie_id:
        cookie_id = str(uuid.uuid4())

    if city:
        SearchHistory.objects.create(city=city, cookie_id=cookie_id)

    forecast = []
    error = None

    last_cities_json = request.COOKIES.get("last_cities", "[]")

    try:
        last_cities = json.loads(last_cities_json)
    except json.JSONDecodeError:
        last_cities = []

    if city:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}
        )

        if geo_response.ok:
            geo_json = geo_response.json()
            results = geo_json.get("results", [])

            if results:
                location = results[0]
                lat, lon = location.get("latitude"), location.get("longitude")

                weather_response = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "daily": "temperature_2m_max,temperature_2m_min",
                        "timezone": "auto"
                    }
                )

                if weather_response.ok:
                    data = weather_response.json()
                    forecast = list(zip(
                        data["daily"]["time"],
                        data["daily"]["temperature_2m_min"],
                        data["daily"]["temperature_2m_max"]
                    ))

                    city_title = city.lower().title()

                    if city_title in last_cities:
                        last_cities.remove(city_title)

                    last_cities.insert(0, city_title)
                    last_cities = last_cities[:3]
                else:
                    error = "Ошибка получения погоды"
            else:
                error = "Город не найден"
        else:
            error = "Ошибка геокодирования"

    context = {
        "forecast": forecast,
        "city": city.lower().title() if city else None,
        "error": error,
        "last_cities": last_cities if not city else []
    }

    response = render(request, "weather/index.html", context)

    if city:
        response.set_cookie("last_cities", json.dumps(last_cities), max_age=365*24*60*60)

    return response


def city_autocomplete(request):
    term = request.GET.get("term", None)
    results = []

    if term:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": term, "count": 5}
        )

        if geo_response.ok:
            geo_json = geo_response.json()

            for loc in geo_json.get("results", []):
                name = loc.get("name")
                country = loc.get("country")
                results.append(f"{name}, {country}")

    return JsonResponse(results, safe=False)
