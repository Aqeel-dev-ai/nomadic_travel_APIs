from django.db import models
from django.utils import timezone
import random
import string

# Create your models here.

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, choices=[
        ('REGISTRATION', 'Registration'),
        ('PASSWORD_RESET', 'Password Reset')
    ])

    @classmethod
    def generate_otp(cls, email, purpose):
        # Delete any existing OTPs for this email and purpose
        cls.objects.filter(email=email, purpose=purpose).delete()
        
        # Generate a 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Create new OTP record
        otp_obj = cls.objects.create(
            email=email,
            otp=otp,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
            purpose=purpose
        )
        return otp_obj

    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at
