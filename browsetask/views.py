from django.views.generic import ListView, DetailView
from .models import Post, Offer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import PostSerializer, OfferSerializer
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework.exceptions import NotFound



class HomePage(ListView):
    http_method_names = ["get"]
    template_name = "browsetask/homepage.html"
    model = Post
    context_object_name = "posts"
    queryset = Post.objects.all().order_by('-id')[0:30] # loads 30 views at a time

# When you click on the post this will show up
class PostDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "browsetask/detail.html"
    model = Post
    context_object_name = "post"


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


class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        image_file = request.FILES.get("image")  # ✅ Retrieve image from request.FILES

        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            post = serializer.save(author=request.user)  # ✅ Save post first

            if image_file:
                post.image = image_file  # ✅ Assign image separately
                post.save()  # ✅ Save post again with image
            
            return Response(PostSerializer(post, context={'request': request}).data, status=201)

        return Response(serializer.errors, status=400)
    
    def patch(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        # Remove read-only fields from request data
        readonly_fields = ['author_username', 'author_profile', 'offers', 'created_at']
        data = {key: value for key, value in request.data.items() if key not in readonly_fields}

        serializer = PostSerializer(post, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
    # Alternative Fix: Mark read-only fields properly in the serializer
    # You can explicitly mark non-model fields as read-only in your PostSerializer (which you're mostly doing already, so this is just for clarity):

    # author_username = serializers.CharField(source='author.username', read_only=True)

    
    # def patch(self, request, pk):
    #     try:
    #         post = Post.objects.get(pk=pk)
    #     except Post.DoesNotExist:
    #         return Response({"error": "Post not found"}, status=404)

    #     serializer = PostSerializer(post, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)

    #     return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        # Optional: check if the user is the author
        if post.author != request.user:
            return Response({"error": "You do not have permission to delete this post."}, status=403)

        post.delete()
        return Response(status=204)

class PublicPostListView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}