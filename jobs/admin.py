from django.contrib import admin

from .models import Job, CandidateProfile, JobApplication

admin.site.register(Job)
admin.site.register(CandidateProfile)
admin.site.register(JobApplication)

# Register your models here.
