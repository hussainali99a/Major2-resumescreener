from django.db import models
from accounts.models import User

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    title = models.CharField(max_length=255)
    description = models.TextField()
    profile = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('UNDER_REVIEW', 'Under Review'),
        ('NOT_SCREENED', 'Not Screened'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Basic Info
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Resume & File
    resume_file = models.FileField(upload_to='resumes/')
    resume_text = models.TextField(blank=True)
    file_hash = models.CharField(max_length=64)

    # Profiles
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)

    # AI Extracted Insights
    extracted_skills = models.JSONField(default=list, blank=True)
    demonstrated_skills = models.JSONField(default=list, blank=True)
    listed_skills_only = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    gaps = models.JSONField(default=list, blank=True)
    experience = models.FloatField(default=0)
    summary = models.TextField(blank=True)
    match_score = models.FloatField(default=0)
    recommendation = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_SCREENED')
    is_screened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'file_hash')

    def __str__(self):
        return f"{self.name} - {self.job.title}"
    

class DecisionLog(models.Model):
    ACTION_CHOICES = [
        ('ACCEPT', 'Accept'),
        ('REJECT', 'Reject'),
        ('HOLD', 'Hold'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class Interview(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    meeting_link = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    

