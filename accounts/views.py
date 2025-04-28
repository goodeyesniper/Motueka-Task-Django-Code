from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import ProfileSerializer, UserProfileSerializer, AlbumSerializer, AlbumImageSerializer

from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import update_session_auth_hash

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions
from .models import Profile, UserProfile, Album, AlbumImage

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from django.contrib.auth.models import User
from .models import Review, Profile


@csrf_exempt
def submit_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reviewer = request.user  # Assuming user is authenticated
        profile = Profile.objects.get(user__username=data["username"])
        rating = data["rating"]
        comment = data["comment"]

        review = Review.objects.create(reviewer=reviewer, profile=profile, rating=rating, comment=comment)
        return JsonResponse({"message": "Review submitted successfully!"})

def get_reviews(request, username):
    profile = Profile.objects.get(user__username=username)
    reviews = profile.reviews.all()
    data = [{"reviewer": review.reviewer.username, "rating": review.rating, "comment": review.comment, "created_at": review.created_at} for review in reviews]
    return JsonResponse(data, safe=False)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        # Ensure all fields are provided
        if not username or not email or not password or not confirm_password:
            return Response({"error": "All fields are required."}, status=400)

        # Ensure passwords match
        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        # Ensure unique username and email
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=400)

        # Create user with hashed password
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  # Hash password before saving
        )

        # Generate authentication token
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"message": "Registration successful!", "token": token.key}, status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access the login API

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=200)
        return Response({"error": "Invalid credentials"}, status=400)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Remove token or session if you're using token-based authentication
        request.user.auth_token.delete()  # Deletes the user's auth token
        return Response({"message": "Logged out successfully"}, status=200)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        profile.last_seen = now()
        profile.save()

        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class PublicUserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            profile = user.profile
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


    
# This is the key part: serializer = ProfileSerializer(profile, context={'request': request})
# If you skip the context={'request': request}, Django can’t build the full image URL (it only gives you /media/profiles/me.jpg, not the full path like http://127.0.0.1:8000/media/...).

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to request reset links

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

            # Generate password reset token
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"http://127.0.0.1:3000/reset-password/{uidb64}/{token}"  # React frontend URL

            # Send email
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                "admin@yourwebsite.com",
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent!"}, status=200)

        except User.DoesNotExist:
            return Response({"error": "No account found with this email."}, status=400)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        profile = user.profile

        # Update fields if provided
        profile.full_name = request.data.get("full_name", profile.full_name)
        profile.date_of_birth = request.data.get("date_of_birth", profile.date_of_birth)
        profile.address = request.data.get("address", profile.address)
        profile.contact_number = request.data.get("contact_number", profile.contact_number)

         # 🔹 Ensure email is updated in BOTH `User` and `Profile`
        new_email = request.data.get("email")
        if new_email:
            user.email = new_email
            profile.email = new_email  # ✅ Sync email with Profile
            user.save()

        profile.save()

        return Response({"message": "Profile updated successfully!"})
    
class UploadProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ Handle file uploads

    def post(self, request):
        profile = request.user.profile
        image = request.FILES.get("image")  # ✅ Get image from request

        if image:
            profile.image = image
            profile.save()
            return Response({"message": "Profile image updated successfully!"})
        return Response({"error": "No image provided"}, status=400)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # 🔹 Validate current password
        if not user.check_password(current_password):
            return Response({"error": "Incorrect current password"}, status=400)

        # 🔹 Validate new password match
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)

        # 🔹 Change password
        user.set_password(new_password)
        user.save()

        # 🔹 Keep the user logged in after password change
        update_session_auth_hash(request, user)

        return Response({"message": "Password updated successfully!"})

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlbumImageViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        album_id = self.request.query_params.get("album")
        queryset = AlbumImage.objects.filter(album__user=self.request.user)
        if album_id:
            queryset = queryset.filter(album__id=album_id)
        return queryset

    def perform_create(self, serializer):
        album_id = self.request.data.get('album')
        album = Album.objects.get(id=album_id, user=self.request.user)
        serializer.save(album=album)
