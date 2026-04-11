from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import SignupForm, LoginForm
from .models import Job, Candidate
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse



# ✅ Correct way to use User model
User = get_user_model()


# ----------------------
# HOME / LANDING
# ----------------------

def home(request):
    return render(request, 'home.html')


# ----------------------
# AUTH
# ----------------------

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ IMPORTANT: set username = email
            user.username = form.cleaned_data['email']
            user.save()

            print("User created:", user.email)

            # ✅ redirect works here
            return redirect('login')
        else:
            print(form.errors)  # debug errors
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            print("Trying login:", email, password)

            # ✅ FIX: use username=email
            user = authenticate(request, username=email, password=password)

            if user is not None:
                print("Authenticated:", user.email)

                login(request, user)

                # ✅ redirect to dashboard
                return redirect('dashboard')
            else:
                print("Authentication failed")
                form.add_error(None, "Invalid email or password")
        else:
            print(form.errors)
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


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

    return render(request, 'dashboard.html', context)


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


    return render(request, 'job.html', {
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

        return redirect(f'/candidates/?job_id={job_id}')

    return render(request, 'candidates.html', {
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