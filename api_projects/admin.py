from django.contrib import admin

from api_projects.models import Project, Issue, DateUpdateTask, IssueAttachment


admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(IssueAttachment)
admin.site.register(DateUpdateTask)
