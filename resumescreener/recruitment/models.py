from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # still required internally

    def __str__(self):
        return self.email

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    # job_id = models.CharField(max_length=20)
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
        
    ]
    status = models.CharField(
        max_length=50,
        choices=[
            ('Screening', 'Screening'),
            ('Shortlisted', 'Shortlisted'),
            ('Rejected', 'Rejected')
        ],
        default='Screening'
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    resume_file = models.FileField(upload_to='resumes/')
    file_hash = models.CharField(max_length=64, unique=True)

    skills = models.TextField(blank=True)
    experience = models.IntegerField(default=0)

    linkedin = models.URLField(blank=True, null=True)

    match_score = models.FloatField()
    summary = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNDER_REVIEW')

    created_at = models.DateTimeField(auto_now_add=True)
    
    resume_text = models.TextField(blank=True)

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
    
    

# class Job(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     profile = models.CharField(max_length=255)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)



