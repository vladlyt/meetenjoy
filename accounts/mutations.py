import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType

from accounts.models import User
from accounts.serializers import UserSerializer


class UpdateUserMutation(SerializerMutation):
    class Meta:
        serializer_class = UserSerializer
        model_operations = ['update']

    @classmethod
    def mutate_and_get_payload(cls, root, info: graphene.ResolveInfo, **input):
        user = info.context.user
        if not user.is_authenticated:
            errors = ErrorType.from_errors({"user": ["User is not Authenticated"]})
        else:
            return super().mutate_and_get_payload(root, info, **input, id=user.id)
        return cls(errors=errors)


class DeleteUserMutation(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        ok = user.is_authenticated and user.id == kwargs.get("id")
        if not ok:
            return cls(ok=ok)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return cls(ok=False)
        user.is_active = False
        user.save()
        return cls(ok=True)


class UserMutations(graphene.ObjectType):
    user = UpdateUserMutation.Field()
    delete_user = DeleteUserMutation.Field()
