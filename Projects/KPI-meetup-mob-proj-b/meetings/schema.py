import graphene

from graphene_django import DjangoObjectType
from meetings.models import Meeting, Tag
from meetings.views import MeetingSearchView


class MeetingType(DjangoObjectType):
    class Meta:
        model = Meeting


class TagType(DjangoObjectType):
    class Meta:
        model = Tag


class Query:
    meetings = graphene.List(
        MeetingType,
        title=graphene.String(),
        desc=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    meeting = graphene.Field(MeetingType, id=graphene.Int(), title=graphene.String())

    tags = graphene.List(
        TagType,
        name=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    tag = graphene.Field(TagType, id=graphene.Int(), name=graphene.String())

    def resolve_meetings(self, info, **kwargs):
        offset = kwargs.get("offset", 0)
        meetings = MeetingSearchView().get_queryset_by_args(kwargs.get("title", ""), kwargs.get("desc", ""))
        limit = kwargs.get("limit", len(meetings))
        return meetings[offset:offset+limit]

    def resolve_meeting(self, info, **kwargs):
        id = kwargs.get('id')
        title = kwargs.get('title')
        if id is not None:
            return Meeting.objects.get(pk=id)
        if title is not None:
            return Meeting.objects.get(title__icontains=title)
        return None

    def resolve_tags(self, info, **kwargs):
        offset = kwargs.get("offset", 0)
        name = kwargs.get("name")
        tags = Tag.objects.all()
        if name:
            tags = tags.filter(name=name)
        limit = kwargs.get("limit", len(tags))
        return tags[offset:offset+limit]

    def resolve_tag(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if id is not None:
            return Tag.objects.get(pk=id)
        if name is not None:
            return Tag.objects.get(name=name)
        return None
