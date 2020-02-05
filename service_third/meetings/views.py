from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from meetings.loader import DOUApi


class LoadMeetings(APIView):
    permission_classes = []
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        meetings = DOUApi().get_meetings()
        _status = status.HTTP_200_OK
        if meetings is None:
            _status = status.HTTP_400_BAD_REQUEST
            meetings = {"detail": "Meetings are currently loading"}
        return Response(meetings, status=_status)

