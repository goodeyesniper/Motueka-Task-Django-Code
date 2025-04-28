from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, LogoutView, UserProfileView, RegisterView, ForgotPasswordView, UpdateProfileView, ChangePasswordView, UploadProfileImageView, UserProfileViewSet, AlbumViewSet, AlbumImageViewSet, PublicUserProfileView, submit_review, get_reviews


app_name = "accounts"

router = DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)
router.register(r'albums', AlbumViewSet, basename='albums')
router.register(r'album-images', AlbumImageViewSet, basename='album-images')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="api_forgot_password"),
    path('api/profile/update/', UpdateProfileView.as_view(), name='api_profile_update'),
    path("api/password/change/", ChangePasswordView.as_view(), name="api_password_change"),
    path("api/profile/upload-image/", UploadProfileImageView.as_view(), name="api_profile_upload"),

    path('api/public-user-profile/<str:username>/', PublicUserProfileView.as_view(), name='api_public_user_profile'),


    path("profile/review/", submit_review, name="submit_review"),
    path("profile/<str:username>/reviews/", get_reviews, name="get_reviews"),

]