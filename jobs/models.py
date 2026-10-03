from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume_file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    match_score = models.FloatField(default=0.0, help_text="Semantic match score percentage")
    status = models.CharField(
        max_length=20, 
        choices=[('Applied', 'Applied'), ('Reviewing', 'Reviewing'), ('Interview', 'Interview'), ('Rejected', 'Rejected')],
        default='Applied'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} -> {self.job.title} ({self.match_score}%)"

# Create your models here.
