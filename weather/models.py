from django.db import models
from django.contrib.auth.models import User


class SearchHistory(models.Model):
    city = models.CharField(max_length=100)
    cookie_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
