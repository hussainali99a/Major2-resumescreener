from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from recruiter.models import Job, Candidate, User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from recruiter.utils import extract_text_from_resume
import hashlib

# ----------------------
# DASHBOARD
# ----------------------

@login_required(login_url='login')
def dashboard(request):
    jobs = Job.objects.all().order_by('-created_at')
    candidates = Candidate.objects.all().order_by('-created_at')

    context = {
        'jobs_count': jobs.count(),
        'candidates_count': candidates.count(),
        'recent_jobs': jobs[:5],
        'recent_candidates': candidates[:5],
    }

    return render(request, 'recruiter/dashboard.html', context)


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

        return redirect('jobs')


    # SEARCH
    query = request.GET.get('q', '')
    jobs = Job.objects.filter(user=request.user)

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


    return render(request, 'recruiter/job.html', {
        'page_obj': page_obj,
        'query': query
    })
    

@login_required
def candidates_view(request, job_id=None):
    jobs = Job.objects.filter(user=request.user)
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
            return redirect(f'jobs/{job_id}/candidates/')

        # 🔐 hash file (avoid duplicates)
        file_hash = hashlib.sha256(resume.read()).hexdigest()
        resume.seek(0)

        if Candidate.objects.filter(file_hash=file_hash, job_id=job_id).exists():
            return redirect(f'jobs/{job_id}/candidates/')

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
            status="UNDER_REVIEW"
        )

        return redirect(f'/hr/jobs/{job_id}/candidates/')

    jobs = Job.objects.filter(user=request.user)
    return render(request, 'recruiter/candidates.html', {
        'jobs': jobs,
        'candidates': candidates,
        'selected_job': job_id,
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'avg_per_job': round(avg_per_job, 2)
    })

@login_required
def job_candidates_api(request, job_id):
    candidates = Candidate.objects.filter(job_id=job_id)

    data = []
    for c in candidates:
        data.append({
            "name": c.name,
            "email": c.email,
            "score": c.match_score,
            "status": c.status
        })

    return JsonResponse(data, safe=False)

@login_required
def candidate_detail_api(request, id):
    c = Candidate.objects.get(id=id)

    return JsonResponse({
        "name": c.name,
        "email": c.email,
        "summary": c.summary,
        "score": c.match_score,
        "status": c.status,
        "resume_url": c.resume_file.url
})
    
@login_required
def job_detail_api(request, job_id):
    job = Job.objects.get(id=job_id, user=request.user)

    return JsonResponse({
        "title": job.title,
        "profile": job.profile,
        "description": job.description,
        "created_at": job.created_at.isoformat()
    })

@login_required
def screen_single(request, job_id, id):
    candidate = Candidate.objects.get(id=id)

    # 🔥 Replace with LLM later
    candidate.match_score = 78
    candidate.summary = "Good match based on skills"
    candidate.status = "UNDER_REVIEW"
    candidate.save()

    return redirect(f"/hr/jobs/{job_id}/candidates/")


@login_required
def screen_all(request, job_id):
    candidates = Candidate.objects.filter(match_score=0, job_id=job_id)

    for c in candidates:
        c.match_score = 75
        c.summary = "Auto screened"
        c.status = "UNDER_REVIEW"
        c.save()

    return redirect(f"/hr/jobs/{job_id}/candidates/")