from accounts.views import (
    RegistrationAPIView,
    RetrieveUpdateUserAPIView,
    CreateRateLectorView,
    UpdateRateLectorView,
    LectorListAPIView,
    UpgradeToLectorView, RetrieveUserAPIView)
from django.urls import path

urlpatterns = [
    path('me/', RetrieveUpdateUserAPIView.as_view()),
    path('registration/', RegistrationAPIView.as_view()),
    path('user/<int:pk>/', RetrieveUserAPIView.as_view()),
    path('lectors/', LectorListAPIView.as_view()),
    path('upgrade-to-lector/', UpgradeToLectorView.as_view()),
    path('rate/', CreateRateLectorView.as_view()),
    path('rate/<int:pk>/', UpdateRateLectorView.as_view()),
]
