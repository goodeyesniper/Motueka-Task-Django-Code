from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView
from notifications.models import Notification
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Offer, Post
from .serializers import OfferSerializer, PostSerializer


class HomePage(ListView):
    http_method_names = ["get"]
    template_name = "browsetask/homepage.html"
    model = Post
    context_object_name = "posts"
    queryset = Post.objects.all().order_by('-id')[0:30] # loads 30 views at a time

class PostDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "browsetask/detail.html"
    model = Post
    context_object_name = "post"

class AssignTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({'error': 'You are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username')

        # Reset logic
        if username == "reset":
            if post.assigned_to:
                Notification.objects.filter(user=post.assigned_to, task=post).delete()  # ✅ safer deletion
            post.assigned_to = None
            post.status = "open"
            post.save()
            return Response({'message': 'Task assignment reset', 'status': 'open'}, status=status.HTTP_200_OK)

        try:
            user_to_assign = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete old notification for this task (if any)
        Notification.objects.filter(user=user_to_assign, task=post).delete()  # ✅ clean match

        post.assigned_to = user_to_assign
        post.status = "assigned"
        post.save()

        # Create the new notification with proper task reference
        Notification.objects.create(
            user=user_to_assign,
            task=post,  # ✅ This is the key part
            message=f"Congratulations! You have been assigned to the task: {post.task_title}"
        )

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostDetailAPI(APIView):
    permission_classes = [AllowAny]  # Or use IsAuthenticated if the post is private

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound(detail="Post not found")

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

class OfferCreateView(generics.CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        serializer.save(user=self.request.user, post_id=post_id)

class OfferListView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs.get("pk")
        return Offer.objects.filter(post_id=post_id).order_by("created_at") # order by latest post being on top and the oldest at the bottom
    
class OfferAuthorsView(APIView):
    def get_permissions(self):
        # Allow both authenticated and unauthenticated users
        if self.request.method == 'GET':
            return [AllowAny()]  # Public access for GET requests
        return [IsAuthenticated()]  # Require authentication for other methods (POST, DELETE, PATCH, etc.)
    
    def get(self, request, post_id):  
        try:
            post = Post.objects.get(pk=post_id)  # Fetch the post to get the author
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        offers = Offer.objects.filter(post_id=post_id).select_related("user__profile")

        # Exclude the author from the list
        offer_authors = [
            {
                "full_name": offer.user.profile.full_name,
                "user_id": offer.user.id,
                "username": offer.user.username
            }
            for offer in offers if offer.user != post.author  # Filter out the post author
        ]

        return Response(offer_authors)

class PostListView(APIView):
    def get_permissions(self):
        # Allow both authenticated and unauthenticated users
        if self.request.method == 'GET':
            return [AllowAny()]  # Public access for GET requests
        return [IsAuthenticated()]  # Require authentication for other methods (POST, DELETE, PATCH, etc.)

    def get(self, request):
        # Both authenticated and unauthenticated users can view posts
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Only authenticated users can post tasks
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required to post."}, status=403)

        data = request.data.copy()
        image_file = request.FILES.get("image")

        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            post = serializer.save(author=request.user)  # Associate post with the user

            if image_file:
                post.image = image_file  # Save image if provided
                post.save()

            return Response(PostSerializer(post, context={'request': request}).data, status=201)

        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        # Check if the post exists
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        # Ensure the user is the author of the post
        if post.author != request.user:
            return Response({"error": "You do not have permission to edit this post."}, status=403)

        # Remove read-only fields from request data
        readonly_fields = ['author_username', 'author_profile', 'offers', 'created_at']
        data = {key: value for key, value in request.data.items() if key not in readonly_fields}

        serializer = PostSerializer(post, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        # Check if the post exists
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        # Ensure the user is the author of the post
        if post.author != request.user:
            return Response({"error": "You do not have permission to delete this post."}, status=403)

        post.delete()
        return Response(status=204)