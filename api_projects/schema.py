import graphene
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
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
# Note: because of the large number of classes, consider separated files in future.


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


class DeleteObjectInput(graphene.InputObjectType):
    pk = graphene.ID(required=True)


class CreateProjectInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    members = graphene.List(graphene.ID)


class UpdateProjectInput(CreateProjectInput):
    pk = graphene.ID(required=True)
    name = graphene.String(required=False)


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


class CreateIssueInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    due_date = graphene.DateTime(required=True)
    status = graphene.String()
    assigne = graphene.ID()
    project = graphene.ID(required=True)


class UpdateIssueInput(CreateIssueInput):
    pk = graphene.ID(required=True)
    title = graphene.String(required=False)
    due_date = graphene.DateTime(required=False)
    project = graphene.ID(required=False)


class CreateIssueMutation(graphene.Mutation):
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


class UpdateIssueMutation(CreateIssueMutation):
    class Arguments:
        issue_data = UpdateIssueInput(required=True)

    @classmethod
    def mutate(cls, root, info, issue_data=None, **kwargs):
        issue = get_object_or_404(Issue, pk=issue_data.pk)
        # Serializer always requires `required` fields,
        # so if these are not given in request,
        # we can still get them from instance.
        instance_dict = model_to_dict(issue)
        instance_dict.update(issue_data)

        serializer = IssueSerializer(issue, data=instance_dict)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

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


class CreateIssueAttachmentMutation(graphene.Mutation):
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


class DeleteObjectMutation(graphene.Mutation):
    class Arguments:
        data = DeleteObjectInput(required=True)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, data=None, **kwargs):
        raise NotImplementedError(
            "Inherited classes must implement this method.")


class DeleteProjectMutation(DeleteObjectMutation):
    @classmethod
    def mutate(cls, root, info, data=None, **kwargs):
        instance = get_object_or_404(Project, pk=data.pk)
        instance.delete()
        return cls(message=f"Deleted object with pk: {data.pk}.")


class DeleteIssueMutation(DeleteObjectMutation):
    @classmethod
    def mutate(cls, root, info, data=None, **kwargs):
        instance = get_object_or_404(Issue, pk=data.pk)
        instance.delete()
        return cls(message=f"Deleted object with pk: {data.pk}.")


class DeleteAttachmentMutation(DeleteObjectMutation):
    @classmethod
    def mutate(cls, root, info, data=None, **kwargs):
        instance = get_object_or_404(IssueAttachmentNode, pk=data.pk)
        instance.delete()
        return cls(message=f"Deleted object with pk: {data.pk}.")


class Mutation(graphene.ObjectType):
    create_project = CreateProjectMutation.Field()
    update_project = UpdateProjectMutation.Field()
    delete_project = DeleteProjectMutation.Field()

    create_issue = CreateIssueMutation.Field()
    update_issue = UpdateIssueMutation.Field()
    delete_issue = DeleteIssueMutation.Field()

    upload_attachment = CreateIssueAttachmentMutation.Field()
    delete_attachment = DeleteAttachmentMutation.Field()
