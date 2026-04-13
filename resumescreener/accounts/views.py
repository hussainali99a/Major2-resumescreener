from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.forms import SignupForm, LoginForm
from django.contrib.auth.decorators import login_required
from accounts.models import User
from mailer.sender import verify_otp, send_email_otp


@login_required
def verify_otp_view(request):
    if request.method == "POST":
        otp = request.POST.get("otp")

        success, message = verify_otp(request.user, otp)

        if success:
            # 🔥 mark user verified (you should have this field)
            request.user.is_verified = True  # or custom field
            request.user.save()

            return redirect("dashboard")  # ✅ redirect here

        return render(request, "accounts/verify_otp.html", {"error": message})

    return render(request, "accounts/verify_otp.html")


@login_required
def resend_otp(request):
    if request.method == "POST":
        send_email_otp(request.user)
    return redirect("verify_otp")

def home(request):
    return render(request, 'accounts/index.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.username = form.cleaned_data['email']
            user.save()

            print("User created:", user.email)
            send_email_otp(user)
            login(request, user)
            return redirect("verify_otp")
        else:
            form.add_error(None, form.errors.as_text())
            # print(form.errors) 
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            print("Trying login:", email, password)

            user = authenticate(request, username=email, password=password)

            if user is not None:
                print("Authenticated:", user.email)
                login(request, user)
                if not request.user.is_verified:
                    return redirect("resend_otp")

                return redirect('dashboard')
            else:
                print("Authentication failed")
                form.add_error(None, "Invalid email or password")
        else:
            print(form.errors)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

