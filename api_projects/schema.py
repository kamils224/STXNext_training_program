import graphene
from django.shortcuts import get_object_or_404
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
        host = info.context.META.get("HTTP_HOST", None)
        if host is not None:
            return host + parent.file_attachment.url
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


class CreateProjectInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    members = graphene.List(graphene.ID)


class UpdateProjectInput(CreateProjectInput):
    pk = graphene.ID(required=True)
    name = graphene.String(required=False)


class DeleteProjectInput(graphene.InputObjectType):
    pk = graphene.ID()


class CreateProjectMutation(graphene.Mutation):
    class Arguments:
        project_data = CreateProjectInput(required=True)

    pk = graphene.ID()
    name = graphene.String()
    members = graphene.List(UserNode)
    owner = graphene.Field(UserNode)

    @classmethod
    def mutate(cls, root, info, project_data=None, **kwargs):
        user = info.context.user
        serializer = ProjectSerializer(data=project_data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)
        return cls(pk=obj.pk, name=obj.name, members=obj.members.all(), owner=obj.owner)


class UpdateProjectMutation(CreateProjectMutation):
    class Arguments:
        project_data = UpdateProjectInput(required=True)

    @classmethod
    def mutate(cls, root, info, project_data=None, **kwargs):
        project = get_object_or_404(Project, pk=project_data.pk)
        serializer = ProjectSerializer(project, data=project_data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return cls(pk=obj.pk, name=obj.name, members=obj.members.all(), owner=obj.owner)


class DeleteProjectMutation(graphene.Mutation):
    class Arguments:
        project_data = DeleteProjectInput(required=True)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, project_data=None, **kwargs):
        project = get_object_or_404(Project, pk=project_data.pk)
        project.delete()
        return cls(message=f"Deleted object with pk: {[project_data.pk]}.")


class CreateIssueInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    due_date = graphene.DateTime(required=True)
    status = graphene.String()
    assigne = graphene.ID()
    project = graphene.ID(required=True)


class IssueMutation(graphene.Mutation):
    class Arguments:
        issue_data = CreateIssueInput(required=True)

    pk = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    due_date = graphene.DateTime()
    status = graphene.String()
    owner = graphene.Field(UserNode)
    assigne = graphene.Field(UserNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    def mutate(cls, root, info, issue_data=None, **kwargs):
        user = info.context.user
        print(issue_data)
        serializer = IssueSerializer(data=issue_data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=user)

        return cls(
            pk=obj.pk,
            title=obj.title,
            description=obj.description,
            due_date=obj.due_date,
            status=obj.status,
            owner=obj.owner,
            assigne=obj.assigne,
            project=obj.project,
        )


class UploadAttachmentInput(graphene.InputObjectType):
    issue = graphene.ID(required=True)


class IssueAttachmentMutation(graphene.Mutation):
    class Arguments:
        attachment_data = UploadAttachmentInput(required=True)

    attachment = graphene.List(IssueAttachmentNode)

    @classmethod
    def mutate(cls, root, info, attachment_data, **kwargs):
        issue = get_object_or_404(Issue, pk=attachment_data.issue)
        files = info.context.FILES

        # allows to save multiple files at once
        attachments = [
            IssueAttachment(file_attachment=attachment, issue=issue)
            for attachment in files.values()
        ]
        created = IssueAttachment.objects.bulk_create(attachments)
        return cls(attachment=created)


class Mutation(graphene.ObjectType):
    create_project = CreateProjectMutation.Field()
    update_project = UpdateProjectMutation.Field()
    delete_project = DeleteProjectMutation.Field()
    create_issue = IssueMutation.Field()
    upload_attachment = IssueAttachmentMutation.Field()
