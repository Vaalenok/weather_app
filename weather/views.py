import requests
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    city = request.GET.get("city")
    forecast = []
    error = None

    if city:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1
            }
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
                else:
                    error = "Ошибка получения погоды"
            else:
                error = "Город не найден"
        else:
            error = "Ошибка геокодирования"

    context = {
        "forecast": forecast,
        "city": city.lower().title() if city else None,
        "error": error
    }

    return render(request, "weather/index.html", context)


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
