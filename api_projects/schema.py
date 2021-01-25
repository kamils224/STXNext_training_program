import graphene
from rest_framework import status
from graphene.relay import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload


from api_accounts.schema import UserNode
from api_projects.models import Project, Issue, IssueAttachment
from api_projects.serializers import (
    ProjectSerializer,
    IssueSerializer,
    IssueAttachmentSerializer,
)


class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "creation_date": ["exact", "gt", "lt"],
        }
        interfaces = (Node,)

    pk = graphene.Int(source="pk")


class IssueNode(DjangoObjectType):
    class Meta:
        model = Issue
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "description": ["icontains"],
            "status": ["exact"],
            "owner": ["exact"],
        }
        interfaces = (Node,)

    pk = graphene.Int(source="pk")


class IssueAttachmentNode(DjangoObjectType):
    class Meta:
        fields = ["issue", "url", "filename"]
        model = IssueAttachment
        filter_fields = ["issue"]
        interfaces = (Node,)

    pk = graphene.Int(source="pk")
    url = graphene.String()
    filename = graphene.String()

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
    class Arguments:
        pk = graphene.ID()
        name = graphene.String(required=True)
        members = graphene.List(graphene.ID)

    name = graphene.String()
    members = graphene.List(UserNode)
    owner = graphene.Field(UserNode)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        serializer = ProjectSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)
        return cls(name=obj.name, members=obj.members.all(), owner=obj.owner)


class IssueMutation(graphene.Mutation):
    class Arguments:
        pk = graphene.ID()
        title = graphene.String(required=True)
        description = graphene.String()
        due_date = graphene.DateTime(required=True)
        status = graphene.String()
        assigne = graphene.ID()
        project = graphene.ID()

    title = graphene.String()
    description = graphene.String()
    due_date = graphene.DateTime()
    status = graphene.String()
    owner = graphene.Field(UserNode)
    assigne = graphene.Field(UserNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        serializer = IssueSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)

        return cls(
            title=obj.title,
            description=obj.description,
            due_date=obj.due_date,
            status=obj.status,
            owner=obj.owner,
            assigne=obj.assigne,
            project=obj.project,
        )


class IssueAttachmentMutation(graphene.Mutation):
    class Arguments:
        attachment = Upload(required=True)
        issue = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(self, info, attachment, **kwargs):
        print(attachment)
        print(kwargs)

        return cls(success=True)


class Mutation(graphene.ObjectType):
    create_project = ProjectMutation.Field()
    create_issue = IssueMutation.Field()
    upload_attachment = IssueAttachmentMutation.Field()
