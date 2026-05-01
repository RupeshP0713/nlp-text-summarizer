from django.urls import path

from .views import index, keywords_api, summarize_api

urlpatterns = [
    path("", index, name="index"),
    path("api/summarize/", summarize_api, name="summarize_api"),
    path("api/keywords/", keywords_api, name="keywords_api"),
]
