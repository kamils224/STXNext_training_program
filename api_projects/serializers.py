from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from api_projects.models import Project, Issue


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.pk')

    class Meta:
        model = Project
        fields = ["name", "owner"]


class IssueSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.pk')

    class Meta:
        model = Issue
        fields = "__all__"
