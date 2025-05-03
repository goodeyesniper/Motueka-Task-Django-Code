from django.urls import path
from .views import HomePage, PostDetailView, PostListView, PublicPostListView, OfferCreateView, PostDetailAPI

app_name = "browsetask"

urlpatterns = [
    path("", HomePage.as_view(), name="index"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path('api/posts/', PostListView.as_view(), name='post_list'),
    # path('api/posts/<int:pk>/', PostListView.as_view(), name='post_update'),  # ✅ Added endpoint for updating posts
    path('api/public-posts/', PublicPostListView.as_view(), name='public_post_list'),
    path("api/posts/<int:pk>/offers/", OfferCreateView.as_view(), name="offer_create"),

    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='post_detail_api'),
    
]
