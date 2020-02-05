import graphene

from accounts.mutations import UserMutations
from meetings.schema import Query as MeetingsQuery
from meetings.mutations import MeetingMutations
from accounts.schema import Query as AccountsQuery


class Query(MeetingsQuery, AccountsQuery, graphene.ObjectType):
    pass


class Mutation(MeetingMutations, UserMutations):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
