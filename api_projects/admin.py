from django.contrib import admin

from api_projects.models import Project, Issue


admin.site.register(Project)
admin.site.register(Issue)
