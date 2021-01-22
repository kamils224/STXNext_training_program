import graphene

from api_accounts import schema as accounts_schema
from api_projects import schema as projects_schema


class Query(projects_schema.Query, accounts_schema.Query, graphene.ObjectType):
    pass


class Mutation(projects_schema.Mutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
