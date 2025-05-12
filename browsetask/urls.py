from django.urls import path

from .views import (AssignTaskView, HomePage, OfferAuthorsView,
                    OfferCreateView, OfferListView, PostDetailAPI,
                    PostDetailView, PostListView)

app_name = "browsetask"

urlpatterns = [
    path("", HomePage.as_view(), name="index"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path('api/posts/', PostListView.as_view(), name='post_list'),

    path("api/posts/<int:pk>/offers/", OfferCreateView.as_view(), name="offer_create"),
    path("api/posts/<int:pk>/offers/list/", OfferListView.as_view(), name="offer_list"),
    path('api/posts/<int:post_id>/assign/', AssignTaskView.as_view(), name='assign_task'),
    path("api/posts/<int:post_id>/offer-authors/", OfferAuthorsView.as_view(), name="offer-authors"),
   
    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='post_detail_api'),
    
]
