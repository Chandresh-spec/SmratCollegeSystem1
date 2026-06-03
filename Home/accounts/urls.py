from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView,
    ForgotPasswordView, VerifyOTPView, ResetPasswordView,
    SendRegisterOTPView, VerifyRegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),

    # Forgot password flow
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),

    # Registration email verification
    path('send-register-otp/', SendRegisterOTPView.as_view()),
    path('verify-register/', VerifyRegisterView.as_view()),
]
