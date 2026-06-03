from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
import random
import string

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════
# FORGOT PASSWORD FLOW
# ════════════════════════════════════════════════

class ForgotPasswordView(APIView):
    """Step 1: Send OTP to user's registered email for password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email address'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate and cache OTP (expires in 10 minutes)
        otp = generate_otp()
        cache_key = f'forgot_otp_{email}'
        cache.set(cache_key, otp, timeout=600)

        # Send OTP via email
        try:
            send_mail(
                subject='EduHub — Password Reset Code',
                message=f'Your password reset verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, please ignore this email.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to send email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Verification code sent to your email',
        })


class VerifyOTPView(APIView):
    """Step 2: Verify the OTP for password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()

        if not email or not otp:
            return Response(
                {'error': 'Email and OTP are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'forgot_otp_{email}'
        cached_otp = cache.get(cache_key)

        if not cached_otp:
            return Response(
                {'error': 'Verification code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_otp != otp:
            return Response(
                {'error': 'Invalid verification code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as verified (store a verified flag)
        cache.set(f'forgot_verified_{email}', True, timeout=600)

        return Response({
            'message': 'Verification successful',
        })


class ResetPasswordView(APIView):
    """Step 3: Reset password after OTP verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')

        if not email or not otp or not new_password:
            return Response(
                {'error': 'Email, OTP, and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP again for security
        cache_key = f'forgot_otp_{email}'
        cached_otp = cache.get(cache_key)

        if not cached_otp or cached_otp != otp:
            return Response(
                {'error': 'Invalid or expired verification code. Please start over.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Reset the password
        user.set_password(new_password)
        user.save()

        # Clean up cache
        cache.delete(cache_key)
        cache.delete(f'forgot_verified_{email}')

        return Response({
            'message': 'Password reset successfully',
        })


# ════════════════════════════════════════════════
# EMAIL VERIFICATION DURING REGISTRATION
# ════════════════════════════════════════════════

class SendRegisterOTPView(APIView):
    """Send OTP to email for registration verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        username = request.data.get('username', '').strip()

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email or username already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'An account with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if username and User.objects.filter(username=username).exists():
            return Response(
                {'error': 'This username is already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate and cache OTP
        otp = generate_otp()
        cache_key = f'register_otp_{email}'
        cache.set(cache_key, otp, timeout=600)

        # Send OTP via email
        try:
            send_mail(
                subject='EduHub — Email Verification Code',
                message=f'Your email verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nWelcome to EduHub!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to send email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Verification code sent to your email',
        })


class VerifyRegisterView(APIView):
    """Verify OTP and register user in one step."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()

        if not email or not otp:
            return Response(
                {'error': 'Email and verification code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP
        cache_key = f'register_otp_{email}'
        cached_otp = cache.get(cache_key)

        if not cached_otp:
            return Response(
                {'error': 'Verification code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_otp != otp:
            return Response(
                {'error': 'Invalid verification code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP verified — now register the user
        reg_data = {
            'username': request.data.get('username'),
            'email': email,
            'password': request.data.get('password'),
            'role': request.data.get('role', 'student'),
            'mobile_number': request.data.get('mobile_number'),
            'usn': request.data.get('usn'),
            'sem': request.data.get('sem'),
        }

        serializer = RegisterSerializer(data=reg_data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            # Clean up OTP from cache
            cache.delete(cache_key)

            return Response({
                'message': 'Registration successful! Email verified.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)