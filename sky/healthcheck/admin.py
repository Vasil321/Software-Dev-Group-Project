from django.contrib import admin
from .models import UserProfile, Team, Department, HealthCheckSession, Question, Response

admin.site.register(UserProfile)
admin.site.register(Team)
admin.site.register(Department)
admin.site.register(HealthCheckSession)
admin.site.register(Question)
admin.site.register(Response)
