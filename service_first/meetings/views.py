import time

from rest_framework import generics, serializers
import django_filters

from meetings.models import Meeting


class MeetingFilter(django_filters.FilterSet):
    class Meta:
        model = Meeting
        fields = {
            'title': ['exact', 'contains'],
            'description': ['exact', 'contains'],
        }


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = "__all__"


class SearchView(generics.ListAPIView):
    serializer_class = MeetingSerializer
    filterset_class = MeetingFilter
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = []

    def get_queryset(self):
        print("Sleep for 2 sec")
        time.sleep(2)
        return Meeting.objects.all()
