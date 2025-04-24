from django.views.generic import ListView, DetailView
from .models import Post
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import PostSerializer
from rest_framework.response import Response
from rest_framework.generics import ListAPIView


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


class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class PublicPostListView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}


# Alternative
# class PostListView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         posts = Post.objects.all().order_by('-created_at')
#         serializer = PostSerializer(posts, many=True, context={'request': request})
#         return Response(serializer.data)