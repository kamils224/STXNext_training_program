from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from api_projects.models import Project, Issue, IssueAttachment


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.pk")

    class Meta:
        model = Project
        fields = ["name", "owner"]


class IssueSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.pk")
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = "__all__"

    def get_attachments(self, issue):
        hostname = self.context["request"].META["HTTP_HOST"]
        return ({"id": file.pk, "name": str(file), "url": f"{hostname}{file.file_attachment.url}"}
                for file in issue.files.all())


class IssueAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueAttachment
        fields = "__all__"
