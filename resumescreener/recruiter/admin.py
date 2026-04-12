from django.contrib import admin
from .models import Job, Candidate, DecisionLog, Interview


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ( 'id','title', 'profile', 'created_at')
    search_fields = ('title', 'profile')


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'job', 'match_score', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email')


@admin.register(DecisionLog)
class DecisionLogAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'action', 'user', 'created_at')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'scheduled_time', 'meeting_link')