from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Meeting, Tag


class MeetingSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "description",
            "small_description",
            "created_at",
            "date_string",
            "main_photo",
            "photo_url",
            "published_at",
            "start_at",
            "duration",
            "status",
            "location",
            "is_main",
            "from_site",
            "from_url",
            "creator",
            "participants_count",
        )
        read_only_fields = ("created_at", "is_main", "from_site", "from_url")

    def get_participants_count(self, obj):
        return obj.participants.count()


class ReadOnlyMeetingSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "description",
            "small_description",
            "created_at",
            "published_at",
            "start_at",
            "duration",
            "main_photo",
            "photo_url",
            "status",
            "location",
            "is_main",
            "from_site",
            "from_url",
            "related_id",
            "date_string",
            "creator",
            "participants_count",
            "is_subscribed",
        )
        read_only_fields = fields

    def get_participants_count(self, obj):
        return obj.participants.count()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return user in obj.participants.all()

    def create(self, validated_data):
        assert False

    def update(self, instance, validated_data):
        assert False


class SubscribeToMeetingSerializer(serializers.Serializer):
    meeting_id = serializers.IntegerField(required=True)

    def validate_meeting_id(self, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise serializers.ValidationError({"meeting_id": "Invalid meeting_id"})
        user = self.context["request"].user
        if user in meeting.participants.all():
            raise serializers.ValidationError({"user": "User is already subscribed to this meeting"})
        return meeting_id

    def create(self, validated_data):
        user = self.context["request"].user
        meeting_id = validated_data.get("meeting_id")
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.participants.add(user)
        return meeting

    def update(self, instance, validated_data):
        assert False


class UnsubscribeFromMeetingSerializer(serializers.Serializer):
    meeting_id = serializers.IntegerField(required=True)

    def validate_meeting_id(self, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise serializers.ValidationError({"meeting_id": "Invalid meeting_id"})
        user = self.context["request"].user
        if user not in meeting.participants.all():
            raise serializers.ValidationError({"user": "User is not subscribed to this meeting"})
        return meeting_id

    def create(self, validated_data):
        user = self.context["request"].user
        meeting_id = validated_data.get("meeting_id")
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.participants.remove(user)
        return meeting

    def update(self, instance, validated_data):
        assert False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


