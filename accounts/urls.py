from django.urls import path
from .views import LoginView, LogoutView, UserProfileView, RegisterView, ForgotPasswordView, UpdateProfileView, ChangePasswordView, UploadProfileImageView

app_name = "accounts"

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="api_forgot_password"),
    path('api/profile/update/', UpdateProfileView.as_view(), name='api_profile_update'),
    path("api/password/change/", ChangePasswordView.as_view(), name="api_password_change"),
    path("api/profile/upload-image/", UploadProfileImageView.as_view(), name="api_profile_upload"),

]
