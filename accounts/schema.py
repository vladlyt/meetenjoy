import graphene

from graphene_django import DjangoObjectType
from accounts.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query:
    users = graphene.List(
        UserType,
        first_name=graphene.String(),
        last_name=graphene.String(),
        email=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    user = graphene.Field(UserType, id=graphene.Int(), username=graphene.String())

    def resolve_users(self, info, **kwargs):
        offset = kwargs.get("offset", 0)
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        email = kwargs.get("email")
        users = User.objects.all()
        if first_name:
            users = users.filter(first_name__icontains=first_name)
        if last_name:
            users = users.filter(last_name__icontains=last_name)
        if email:
            users = users.filter(email__icontains=email)
        limit = kwargs.get("limit", len(users))
        return users[offset:limit]

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')
        if id is not None:
            return User.objects.get(pk=id)
        if username is not None:
            return User.objects.get(username=username)
        return None
