from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import OTPVerification

User = get_user_model()

@receiver(post_save, sender=User)
def send_registration_otp(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        # Generate OTP
        otp_obj = OTPVerification.generate_otp(
            email=instance.email,
            purpose='REGISTRATION'
        )
        
        # Send email with OTP
        subject = 'Verify your email'
        message = f'Your verification code is: {otp_obj.otp}\n\nThis code will expire in 10 minutes.'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )

def send_password_reset_otp(email):
    # Generate OTP
    otp_obj = OTPVerification.generate_otp(
        email=email,
        purpose='PASSWORD_RESET'
    )
    
    # Send email with OTP
    subject = 'Reset your password'
    message = f'Your password reset code is: {otp_obj.otp}\n\nThis code will expire in 10 minutes.'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return otp_obj 