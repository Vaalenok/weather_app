from django.test import TestCase, Client
from django.urls import reverse
from json import loads

from weather.models import SearchHistory


class WeatherViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_without_city(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_with_city(self):
        city = "New York, United States"
        response = self.client.get(reverse("index"), {"city": city})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, city)

    def test_search_history_saved(self):
        city = "Los Angeles, United States"
        self.client.get(reverse("index"), {"city": city})
        self.assertTrue(SearchHistory.objects.filter(city=city).exists())

    def test_cookie_set_last_city(self):
        city = "Paris, France"
        response = self.client.get(reverse("index"), {"city": city})
        self.assertIn("last_cities", response.cookies)
        self.assertIn(city, response.cookies["last_cities"].value)

    def test_cookie_last_cities_rotation(self):
        cities = ["Tokyo, Japan", "Berlin, Germany", "Madrid, Spain", "Rome, Italy"]

        for city in cities:
            self.client.get(reverse("index"), {"city": city})

        response = self.client.get(reverse("index"), {"city": "London, United Kingdom"})
        self.assertIn("last_cities", response.cookies)

        last_cities = loads(response.cookies["last_cities"].value)
        self.assertLessEqual(len(last_cities), 3)
        self.assertIn("London, United Kingdom", last_cities)
