from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from recruiter.models import Job, Candidate, User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from recruiter.utils import extract_text_from_resume
import hashlib

@login_required(login_url='login')
def dashboard(request):
    jobs = Job.objects.filter(user=request.user, job_type="individual").order_by('-created_at')
    candidates = Candidate.objects.filter(user=request.user, job__job_type="individual").order_by('-created_at')

    context = {
        'jobs_count': jobs.count(),
        'candidates_count': candidates.count(),
        'recent_jobs': jobs[:5],
        'recent_candidates': candidates[:5],
    }

    return render(request, 'candidate/dashboard.html', context)


@login_required(login_url='login')
def jobs_view(request):

    # CREATE JOB
    if request.method == "POST":
        title = request.POST.get('title')
        profile = request.POST.get('profile')
        description = request.POST.get('description')

        Job.objects.create(
            title=title,
            profile=profile,
            description=description,
            user=request.user  # 👈 IMPORTANT
        )

        return redirect('candidate-jobs')


    # SEARCH
    query = request.GET.get('q', '')
    jobs = Job.objects.filter(user=request.user, job_type="individual")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(profile__icontains=query)
        )

    jobs = jobs.order_by('-created_at')


    # PAGINATION
    paginator = Paginator(jobs, 6)  # 6 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'candidate/job.html', {
        'page_obj': page_obj,
        'query': query
    })
    

@login_required
def resumes_view(request, job_id=None):
    jobs = Job.objects.filter(user=request.user, job_type="individual").order_by('-created_at')
    candidates = Candidate.objects.none()

    if job_id:
        candidates = Candidate.objects.filter(job__user=request.user, job_id=job_id)

    # 📊 Analytics
    total_resumes = candidates.count()
    total_jobs = jobs.count()
    avg_per_job = total_resumes / total_jobs if total_jobs > 0 else 0
    
    # ================= UPLOAD =================
    if request.method == "POST":
        resume = request.FILES.get('resume')

        if not resume or not job_id:
            return redirect(f'/jobs/{job_id}/resumes/')

        # 🔐 hash file (avoid duplicates)
        file_hash = hashlib.sha256(resume.read()).hexdigest()
        resume.seek(0)

        if Candidate.objects.filter(file_hash=file_hash, job_id=job_id).exists():
            return redirect(f'/jobs/{job_id}/resumes/')

        # 🧠 Extract text (basic version)
        resume_text, email = extract_text_from_resume(resume)  # create this

        # 🧠 Dummy parsing (replace later with AI)
        name = resume_text.split('\n')[0] if resume_text else "Unknown"

        Candidate.objects.create(
            user=request.user,
            job_id=job_id,
            name=name,
            email=email,
            resume_file=resume,
            file_hash=file_hash,
            resume_text=resume_text,
            match_score=0,
            summary="Pending AI screening",
        )

        return redirect(f'/jobs/{job_id}/resumes/')

    return render(request, 'candidate/resumes.html', {
        'jobs': jobs,
        'candidates': candidates,
        'selected_job': job_id,
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'avg_per_job': round(avg_per_job, 2)
    })

from recruiter.services.chains import run_resume_screening

@login_required
def screen_single(request, job_id, id):
    candidate = Candidate.objects.get(id=id)
    if candidate.is_screened:
        return redirect(f"/jobs/{job_id}/resumes/")
    job = Job.objects.get(id=job_id)

    result = run_resume_screening(
        candidate.resume_text,
        job.description
    )

    candidate.name = result.name or candidate.name
    candidate.email = result.email or candidate.email
    candidate.phone = result.phone or candidate.phone
    candidate.linkedin = result.linkedin
    candidate.github = result.github
    candidate.portfolio = result.portfolio

    candidate.extracted_skills = result.all_skills
    candidate.demonstrated_skills = result.demonstrated_skills
    candidate.listed_skills_only = result.listed_skills_only
    candidate.strengths = result.strengths
    candidate.gaps = result.gaps

    candidate.experience = result.experience_years
    candidate.summary = result.reasoning
    candidate.match_score = result.match_score
    candidate.recommendation = result.recommendation
    candidate.is_screened = True

    if result.recommendation == "ACCEPT":
        candidate.status = "ACCEPTED"
    elif result.recommendation == "REJECT":
        candidate.status = "REJECTED"
    else:
        candidate.status = "UNDER_REVIEW"

    candidate.save()

    return redirect(f"jobs/{job_id}/resumes/")
