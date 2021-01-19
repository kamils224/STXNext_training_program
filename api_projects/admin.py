from django.contrib import admin

from api_projects.models import Project, Issue, DateUpdateTask


admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(DateUpdateTask)
