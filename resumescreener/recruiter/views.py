from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from recruiter.models import Job, Candidate, User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse


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
def candidates_view(request):

    job_id = request.GET.get('job_id')

    jobs = Job.objects.filter(user=request.user)

    candidates = Candidate.objects.filter(user=request.user)

    if job_id:
        candidates = candidates.filter(job_id=job_id)

    if request.method == "POST":
        resume = request.FILES.get('resume')

        Candidate.objects.create(
            user=request.user,
            job_id=job_id,
            name="Parsed Name",
            email="parsed@email.com",
            resume=resume,
            score=75,
            status="Screening"
        )

        return redirect(f'/hr/candidates/?job_id={job_id}')

    return render(request, 'recruiter/candidates.html', {
        'jobs': jobs,
        'candidates': candidates,
        'selected_job': job_id
    })


@login_required
def candidate_detail_api(request, id):
    c = Candidate.objects.get(id=id)

    return JsonResponse({
        "name": c.name,
        "email": c.email,
        "summary": getattr(c, 'summary', "N/A"),
        "score": c.score,
        "status": c.status
    })
    
@login_required
def job_detail_api(request, id):
    job = Job.objects.get(id=id, user=request.user)

    return JsonResponse({
        "title": job.title,
        "profile": job.profile,
        "description": job.description,
        "created_at": job.created_at.strftime("%Y-%m-%d"),
    })