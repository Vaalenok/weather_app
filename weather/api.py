from django.http import JsonResponse
from django.db.models import Count
from .models import SearchHistory


def city_search_stats():
    stats = (
        SearchHistory.objects
        .values("city")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return JsonResponse(list(stats), safe=False)
