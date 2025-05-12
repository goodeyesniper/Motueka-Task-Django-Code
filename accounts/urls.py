from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AlbumImageViewSet, AlbumViewSet, ChangePasswordView,
                    ForgotPasswordView, LoginView, LogoutView,
                    PublicUserProfileView, RegisterView, SubmitReviewView,
                    UserProfileView, UserProfileViewSet, 
                    get_current_user, get_reviews)

app_name = "accounts"

router = DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)
router.register(r'albums', AlbumViewSet, basename='albums')
router.register(r'album-images', AlbumImageViewSet, basename='album-images')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('current-user/', get_current_user, name='get_current_user'),

    path("profile/", UserProfileView.as_view(), name="profile_get_update"),
    path('profile/<str:username>/', UserProfileView.as_view(), name='api_profile'),

    path('register/', RegisterView.as_view(), name='api_register'),
    path("forgot-password/", ForgotPasswordView.as_view(), name="api_forgot_password"),

    path("password/change/", ChangePasswordView.as_view(), name="api_password_change"),

    path('public-user-profile/<str:username>/', PublicUserProfileView.as_view(), name='api_public_user_profile'),
    path('profile/review/', SubmitReviewView.as_view(), name='submit-review'),
    path("profile/<str:username>/reviews/", get_reviews, name="get_reviews"),
]