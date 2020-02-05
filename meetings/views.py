from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.utils.timezone import now
from rest_framework import status, generics
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView, RetrieveAPIView, \
    GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from meetings.tasks import cache_request
from meetenjoy.core import IsLector
from .models import Meeting, MeetingStatus, Cache
from .serializers import (
    MeetingSerializer,
    ReadOnlyMeetingSerializer,
    SubscribeToMeetingSerializer,
    UnsubscribeFromMeetingSerializer,
    SmallMeetingSerializer,
)


class MeetingCreateView(CreateAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated, IsLector]

    class Meta:
        model = Meeting

    def create(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "start_at": request.data.get("start_at") or None,
            "duration": request.data.get("duration") or None,
            "status": request.data.get("status"),
            "location": request.data.get("location"),
            "creator": request.user.id,
        }
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateDestroyMeetingView(RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated, IsLector]

    def get_queryset(self):
        return self.request.user.created_meetings

    class Meta:
        model = Meeting


class RetrieveMeetingView(RetrieveAPIView):
    serializer_class = ReadOnlyMeetingSerializer
    queryset = Meeting.objects.all()

    class Meta:
        model = Meeting


class MeetingListView(ListAPIView):
    serializer_class = ReadOnlyMeetingSerializer
    queryset = Meeting.objects.published()

    class Meta:
        model = Meeting


class MyMeetingListView(ListAPIView):
    serializer_class = ReadOnlyMeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.following_meetings.all()

    class Meta:
        model = Meeting


class SubscribeToMeetingView(GenericAPIView):
    serializer_class = SubscribeToMeetingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class UnsubscribeFromMeetingView(GenericAPIView):
    serializer_class = UnsubscribeFromMeetingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class BaseServiceBuilder(ABC):

    @staticmethod
    @abstractmethod
    def build_meeting(meeting):
        pass


class FirstServiceBuilder(BaseServiceBuilder):

    @staticmethod
    def build_meeting(meeting):
        return Meeting(
            id=-1,
            title=meeting.get("title"),
            description=meeting.get("description"),
            status=MeetingStatus.PUBLISHED,
            is_main=False,
        )


class SecondServiceBuilder(BaseServiceBuilder):

    @staticmethod
    def build_meeting(meeting):
        return Meeting(
            id=-1,
            title=meeting.get("title"),
            description=meeting.get("description"),
            status=MeetingStatus.PUBLISHED,
            is_main=False,
        )


class ThirdServiceBuilder(BaseServiceBuilder):
    @staticmethod
    def build_meeting(meeting):
        return Meeting(
            id=-1,
            related_id=meeting.get("id"),
            from_site="https://dou.ua/",
            from_url=meeting.get("url"),
            title=meeting.get("name"),
            description=meeting.get("description"),
            date_string=meeting.get("date_string"),
            status=MeetingStatus.PUBLISHED,
            is_main=False,
        )


class MeetingSearchView(generics.ListAPIView):
    serializer_class = SmallMeetingSerializer
    permission_classes = []

    def _get_from_url(self, url, params=None, retries=1):
        if params is None:
            params = {}
        try:
            print(f"Getting from url: {url}")
            cached_request = Cache.objects.get(
                url=url,
                query_params=params,
            )
        except Cache.DoesNotExist:
            print("NOT FROM CACHE, CASHING")
            cache_request.delay(url=url, params=params)
            return []
        except Cache.MultipleObjectsReturned:
            cached_request = Cache.objects.filter(
                url=url,
                query_params=params,
            ).first()
            Cache.objects.filter(
                url=url,
                query_params=params,
            ).exclude(pk=cached_request.pk).delete()
        if cached_request.expires_after < now():
            cached_request.delete()
            print("NOT FROM CACHE, CASHING")
            cache_request.delay(url=url, params=params)
            return []
        print(f"FROM CACHE: {cached_request.url}")
        return cached_request.response_json

    def get_meetings_from_first_service(self, title, description, builder):
        url = f"{settings.FIRST_SERVICE_URL}/search/"
        meetings = self._get_from_url(url, params={
            "title__contains": title,
            "description__contains": description,
        }, retries=settings.FIRST_SERVICE_RETRIES)
        return [builder.build_meeting(meeting) for meeting in meetings]

    def get_meetings_from_second_service(self, title, description, builder):
        url = f"{settings.SECOND_SERVICE_URL}/meeting-list/"
        result = self._get_from_url(url, retries=settings.SECOND_SERVICE_RETRIES)
        meetings = filter(lambda m: title in str(m.get("title")) and description in str(m.get("description")),
                          result.get("results") if result else [])
        return [builder.build_meeting(meeting) for meeting in meetings]

    def get_meetings_from_third_service(self, title, description, builder):
        url = f"{settings.THIRD_SERVICE_URL}/load-meetings/"
        result = self._get_from_url(url, retries=settings.THIRD_SERVICE_RETRIES)
        meetings = filter(lambda m: title in str(m.get("name")) and description in str(m.get("description")), result)
        return [builder.build_meeting(meeting) for meeting in meetings]

    def load_services(self):
        return [
            (self.get_meetings_from_first_service, FirstServiceBuilder),
            (self.get_meetings_from_second_service, SecondServiceBuilder),
            (self.get_meetings_from_third_service, ThirdServiceBuilder),
        ]

    def get_queryset_by_args(self, title, description):
        meetings = Meeting.objects.filter(title__icontains=title, description__icontains=description)
        len(meetings)  # executing query
        meetings_from_services = []
        for func, builder in self.load_services():
            meetings_from_services += func(title, description, builder)
        for meeting in meetings_from_services:
            meetings._result_cache.append(meeting)
        return meetings

    def get_queryset(self):
        title = self.request.query_params.get("title", "")
        description = self.request.query_params.get("description", "")
        return self.get_queryset_by_args(title, description)
