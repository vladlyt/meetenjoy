from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import RegisterSerializer, UserSerializer, CreateRateSerializer, ReadUpdateRateSerializer
from meetenjoy.core import IsNotAuthenticated, IsNotLector


class RegistrationAPIView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data, context={"request": request})
            if not serializer.is_valid():
                response_data = serializer.errors
                response_status = status.HTTP_400_BAD_REQUEST
            else:
                user = serializer.save()
                login(request, user)
                response_data = UserSerializer(instance=user).data
                response_status = status.HTTP_201_CREATED
            return Response(response_data, status=response_status)


class RetrieveUserAPIView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = []
    queryset = User.objects.all()


class RetrieveUpdateUserAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class LectorListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_lector=True)


class CreateRateLectorView(CreateAPIView):
    serializer_class = CreateRateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        visitor = request.user
        lector = get_object_or_404(User, id=request.data.get("lector"))
        if not lector.is_lector:
            return Response({"message": "Given lector is not lector"},
                            status=status.HTTP_400_BAD_REQUEST)
        if lector in visitor.rated_lectors.all():
            return Response({"message": "Lector with this id already rated be current visitor"},
                            status=status.HTTP_400_BAD_REQUEST)
        data = {
            "visitor": visitor.id,
            "lector": lector.id,
            "rate": request.data.get("rate"),
            "comment": request.data.get("comment"),
        }
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpgradeToLectorView(APIView):
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsNotLector]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_lector = True
        user.save()


class UpdateRateLectorView(RetrieveUpdateAPIView):
    serializer_class = ReadUpdateRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        visitor = self.request.user
        return visitor.visitor_rates.all()
