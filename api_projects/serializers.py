from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api_accounts.models import User
from api_projects.models import Project, Issue, IssueAttachment


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"

    owner = serializers.ReadOnlyField(source="owner.email")
    assigne = serializers.ReadOnlyField(source="assigne.email")
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, issue):
        request_meta = self.context["request"].META
        has_hostname = "HTTP_HOST" in request_meta
        hostname = request_meta["HTTP_HOST"] if has_hostname else "localhost"
        return (
            {
                "id": file.pk,
                "name": str(file),
                "url": f"{hostname}{file.file_attachment.url}",
            }
            for file in issue.files.all()
        )


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            'members': {'write_only': True}
        }

    owner = serializers.ReadOnlyField(source="owner.pk")
    issues = IssueSerializer(many=True, required=False, read_only=True)
    members_emails = serializers.SerializerMethodField()

    def get_members_emails(self, project):
        # possibility to extend returned values
        return project.members.values("id", "email")


class IssueAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueAttachment
        fields = "__all__"
