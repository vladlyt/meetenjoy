from django.urls import path
from meetings.views import MeetingListView, MeetingDetailView

urlpatterns = [
    path("meeting-list/", MeetingListView.as_view()),
    path("detail/<int:pk>/", MeetingDetailView.as_view())
]
