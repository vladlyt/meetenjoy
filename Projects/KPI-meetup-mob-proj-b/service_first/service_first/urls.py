from django.urls import path
from meetings.views import SearchView

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
]
