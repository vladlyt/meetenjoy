from django.urls import path
from meetings.views import LoadMeetings

urlpatterns = [
    path('load-meetings/', LoadMeetings.as_view()),
]
