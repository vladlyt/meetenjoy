import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType

from meetings.models import Meeting
from meetings.serializers import MeetingSerializer, TagSerializer


class CreateUpdateMeetingMutation(SerializerMutation):
    class Meta:
        serializer_class = MeetingSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def mutate_and_get_payload(cls, root, info: graphene.ResolveInfo, **input):
        user = info.context.user
        if not user.is_authenticated:
            errors = ErrorType.from_errors({"user": ["User is not Authenticated"]})
        elif not user.is_lector:
            errors = ErrorType.from_errors({"user": ["User is not a Lector"]})
        else:
            return super().mutate_and_get_payload(root, info, creator=user.pk, **input)
        return cls(errors=errors)


class DeleteMeetingMutation(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        id = kwargs.get("id")
        ok = user.is_authenticated and user.is_lector and id
        if not ok:
            return cls(ok=ok)
        try:
            meeting = Meeting.objects.get(id=id)
        except Meeting.DoesNotExist:
            return cls(ok=False)
        if not meeting.creator or meeting.creator.pk != user.pk:
            return cls(ok=False)
        meeting.delete()
        return cls(ok=True)


class SubscribeOnMeetingMutation(graphene.Mutation):
    ok = graphene.Boolean()
    error_message = graphene.String()

    class Arguments:
        meeting_id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        meeting_id = kwargs.get("meeting_id")
        ok = user.is_authenticated and meeting_id
        if not ok:
            print(meeting_id)
            return cls(ok=ok, error_message="User is not authenticated")
        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            return cls(ok=False)
        if user in meeting.participants.all():
            return cls(ok=False, error_message="User already subscribed to this meeting")
        meeting.participants.add(user)
        return cls(ok=True)


class CreateUpdateTagMutation(SerializerMutation):
    class Meta:
        serializer_class = TagSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'


class MeetingMutations(graphene.ObjectType):
    meeting = CreateUpdateMeetingMutation.Field()
    delete_meeting = DeleteMeetingMutation.Field()
    meeting_subscribe = SubscribeOnMeetingMutation.Field()
    tag = CreateUpdateTagMutation.Field()
