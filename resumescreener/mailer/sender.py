from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from accounts.models import VerificationCodes
import random
import hashlib

def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

def send_email_otp(user, purpose="email_verification"):
    otp = str(random.randint(100101, 999999))

    # ❗ delete old unused OTPs (important)
    VerificationCodes.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False
    ).delete()

    # create new OTP
    otp_obj = VerificationCodes.objects.create(
        user=user,
        otp=hash_otp(otp),
        purpose=purpose
    )

    html_content = render_to_string(
        "mailer/otp_verification.html",
        {
            "user_name": user.first_name,
            "otp": otp,
        }
    )

    email = EmailMultiAlternatives(
        subject="Your OTP Verification",
        body=f"Your OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return otp_obj


def verify_otp(user, otp, purpose="email_verification"):
    try:
        otp_obj = VerificationCodes.objects.get(
            user=user,
            otp=hash_otp(otp),
            purpose=purpose,
            is_used=False
        )
    except VerificationCodes.DoesNotExist:
        return False, "Invalid OTP"

    if otp_obj.is_expired():
        return False, "OTP expired"

    # mark as used
    otp_obj.is_used = True
    otp_obj.save()

    return True, "OTP verified successfully"