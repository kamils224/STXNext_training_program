import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from api_accounts.models import User


class UserNode(DjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = User
        filter_fields = "__all__"
        interfaces = (Node,)


class Query(graphene.ObjectType):
    user = Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)
