from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .models import OTPVerification
from .signals import send_password_reset_otp

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Custom token refresh endpoint that handles user not found cases
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {"detail": "Refresh token is required", "code": "token_missing"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token_obj = OutstandingToken.objects.filter(token=refresh_token).first()

        if not token_obj:
            return Response(
                {"detail": "Token is invalid or expired", "code": "token_not_valid"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Check if user still exists
            user = User.objects.get(id=token_obj.user.id)
        except User.DoesNotExist:
            token_obj.blacklist()  # blacklist the token if user is deleted
            return Response(
                {"detail": "User no longer exists", "code": "user_not_found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Proceed with refreshing token
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    except (TokenError, InvalidToken):
        return Response(
            {"detail": "Token is invalid or expired", "code": "token_not_valid"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {"detail": str(e), "code": "token_error"},
            status=status.HTTP_400_BAD_REQUEST
        )

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    if not email or not otp:
        return Response(
            {'error': 'Email and OTP are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # First verify the OTP
        otp_obj = OTPVerification.objects.get(
            email=email,
            otp=otp,
            purpose='REGISTRATION',
            is_verified=False
        )
        
        if not otp_obj.is_valid():
            return Response(
                {'error': 'OTP has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the most recently created inactive user with this email
        try:
            user = User.objects.filter(
                email=email,
                is_active=False
            ).latest('date_joined')
        except User.DoesNotExist:
            return Response(
                {'error': 'No pending verification found for this email'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Activate user
        user.is_active = True
        user.save()
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        return Response({'message': 'Email verified successfully'})
        
    except OTPVerification.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if any active user exists with this email
    if not User.objects.filter(email=email, is_active=True).exists():
        return Response(
            {'error': 'No active account found with this email'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    send_password_reset_otp(email)
    return Response({'message': 'Password reset OTP sent successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    
    if not all([email, otp, new_password]):
        return Response(
            {'error': 'Email, OTP, and new password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp_obj = OTPVerification.objects.get(
            email=email,
            otp=otp,
            purpose='PASSWORD_RESET',
            is_verified=False
        )
        
        if not otp_obj.is_valid():
            return Response(
                {'error': 'OTP has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the most recently created active user with this email
        try:
            user = User.objects.filter(
                email=email,
                is_active=True
            ).latest('date_joined')
        except User.DoesNotExist:
            return Response(
                {'error': 'No active account found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        return Response({'message': 'Password reset successfully'})
        
    except OTPVerification.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    """
    Get authenticated user details
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'date_joined': user.date_joined
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint that blacklists the refresh token
    """
    try:
        # Get the refresh token from the request body
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required", "code": "token_missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify that the token exists and belongs to the current user
        try:
            token = OutstandingToken.objects.get(token=refresh_token)
            if token.user_id != request.user.id:
                return Response(
                    {"detail": "Token does not belong to the current user", "code": "token_user_mismatch"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except OutstandingToken.DoesNotExist:
            return Response(
                {"detail": "Token is invalid or expired", "code": "token_not_valid"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Blacklist the token
        BlacklistedToken.objects.get_or_create(token=token)
        
        return Response(
            {
                "detail": "Successfully logged out",
                "code": "logout_success",
                "user_id": request.user.id
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"detail": str(e), "code": "logout_error"},
            status=status.HTTP_400_BAD_REQUEST
        )
