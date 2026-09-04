from django.urls import path


from .views import (
    ProfileView,
    RegisterView,
    LoginView,
    ForgotPasswordRequestView,
    ForgotPasswordConfirmView,
    UpdateProfileView,
    CustomTokenRefreshView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/forgot-password/request/', ForgotPasswordRequestView.as_view(), name='forgot-password-request'),
    path('auth/forgot-password/confirm/', ForgotPasswordConfirmView.as_view(), name='forgot-password-confirm'),


     path('profile/', ProfileView.as_view(), name='profile-view'),
    path('profile/update/', UpdateProfileView.as_view(), name='profile-update'),


    path("token/refresh/",CustomTokenRefreshView.as_view(),name="token-refresh")
]