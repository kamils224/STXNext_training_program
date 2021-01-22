import graphene
from rest_framework import status
from graphene.relay import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation

from api_accounts.schema import UserNode
from api_projects.models import Project, Issue, IssueAttachment
from api_projects.serializers import ProjectSerializer


class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = ["name", "owner", "members"]
        interfaces = (Node,)


class IssueNode(DjangoObjectType):
    class Meta:
        model = Issue
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "description": ["exact", "icontains"],
            "status": ["exact"],
        }
        interfaces = (Node,)


class IssueAttachmentNode(DjangoObjectType):
    url = graphene.String()
    filename = graphene.String()

    class Meta:
        fields = ["issue", "url", "filename"]
        model = IssueAttachment
        filter_fields = ["issue"]
        interfaces = (Node,)

    def resolve_url(parent, info):
        meta = info.context.META
        if "HTTP_HOST" in meta:
            return f"{meta['HTTP_HOST']}/{parent.file_attachment}"
        return str(parent.file_attachment)

    def resolve_filename(parent, info):
        return str(parent)


class Query(graphene.ObjectType):
    project = Node.Field(ProjectNode)
    all_projects = DjangoFilterConnectionField(ProjectNode)

    issue = Node.Field(IssueNode)
    all_issues = DjangoFilterConnectionField(IssueNode)

    issue_attachment = Node.Field(IssueAttachmentNode)
    all_issue_attachments = DjangoFilterConnectionField(IssueAttachmentNode)


class CreateProjectMutation(graphene.Mutation):
    name = graphene.String()

    class Arguments:
        name = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        serializer = ProjectSerializer(data=kwargs)
        if serializer.is_valid():
            obj = serializer.save(owner=user)
            print(obj)
            return cls(name=obj)
        return cls(name=None)


class Mutation(graphene.ObjectType):
    create_project = CreateProjectMutation.Field()
