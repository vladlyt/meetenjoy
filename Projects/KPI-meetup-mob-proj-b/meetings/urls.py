from django.conf import settings
from django.urls import path

from meetings import views

urlpatterns = [
    path('meeting/', views.MeetingCreateView.as_view()),
    path('meeting/<int:pk>/', views.UpdateDestroyMeetingView.as_view()),
    path('meeting/<int:pk>/', views.RetrieveMeetingView.as_view()),
    path('my-meetings/', views.MyMeetingListView.as_view()),
    path('all-meetings/', views.MeetingListView.as_view()),
    path('meeting/subscribe/', views.SubscribeToMeetingView.as_view()),
    path('meeting/unsubscribe/', views.UnsubscribeFromMeetingView.as_view()),
]

if settings.USE_SEARCH:

    urlpatterns += [
        path('search/', views.MeetingSearchView.as_view()),
    ]
