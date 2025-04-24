from django.urls import path
from .views import HomePage, PostDetailView, PostListView, PublicPostListView

app_name = "browsetask"

urlpatterns = [
    path("", HomePage.as_view(), name="index"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path('api/posts/', PostListView.as_view(), name='post_list'),
    path('api/public-posts/', PublicPostListView.as_view(), name='public_post_list'),
]