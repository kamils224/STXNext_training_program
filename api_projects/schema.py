import graphene
from rest_framework import status
from graphene.relay import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from api_accounts.schema import UserNode
from api_projects.models import Project, Issue, IssueAttachment
from api_projects.serializers import (
    ProjectSerializer,
    IssueSerializer,
    IssueAttachmentSerializer,
)


class ProjectNode(DjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = Project
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "creation_date": ["exact", "gt", "lt"],
        }
        interfaces = (Node,)


class IssueNode(DjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = Issue
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "description": ["icontains"],
            "status": ["exact"],
            "owner": ["exact"],
        }
        interfaces = (Node,)


class IssueAttachmentNode(DjangoObjectType):
    pk = graphene.Int(source="pk")
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


class ProjectMutation(graphene.Mutation):
    name = graphene.String()
    members = graphene.List(UserNode)
    owner = graphene.Field(UserNode)

    class Arguments:
        name = graphene.String(required=True)
        members = graphene.List(graphene.ID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        serializer = ProjectSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)
        return cls(name=obj.name, members=obj.members.all(), owner=obj.owner)


class IssueMutation(graphene.Mutation):
    title = graphene.String()
    description = graphene.String()
    due_date = graphene.DateTime()
    status = graphene.String()
    owner = graphene.Field(UserNode)
    assigne = graphene.Field(UserNode)
    project = graphene.Field(ProjectNode)

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        due_date = graphene.DateTime(required=True)
        status = graphene.String()
        assigne = graphene.ID()
        project = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        serializer = IssueSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)
        print(obj.owner)
        return cls(
            title=obj.title,
            description=obj.description,
            due_date=obj.due_date,
            status=obj.status,
            owner=obj.owner,
            assigne=obj.assigne,
            project=obj.project,
        )


class Mutation(graphene.ObjectType):
    update_project = ProjectMutation.Field()
    update_issue = IssueMutation.Field()
