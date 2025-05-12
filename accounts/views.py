from django.contrib.auth import authenticate, update_session_auth_hash, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, AlbumImage, Profile, Review, UserProfile
from .serializers import (AlbumImageSerializer, AlbumSerializer,
                          ProfileSerializer, UserProfileSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({
        'username': request.user.username,
        # 'full_name': request.user.get_full_name(),
        # 'email': request.user.email,
        # 'profile_picture': request.user.profile.picture.url if hasattr(request.user, 'profile') else None,
    })

class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reviewer = request.user  # ✅ Logged-in user from token
        username = request.data.get("username")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        if not username or not rating or comment is None:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        Review.objects.create(
            reviewer=reviewer,
            profile=profile,
            rating=rating,
            comment=comment
        )

        return Response({"message": "Review submitted successfully!"}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_reviews(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

    reviews = profile.reviews.all()
    data = [
        {
            "reviewer": review.reviewer.username,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        }
        for review in reviews
    ]
    return Response(data)

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

        try:
            # ✅ Create user only! The profile will be created by the signal.
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )

            # ✅ Generate authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({"message": "Registration successful!", "token": token.key}, status=201)

        except Exception as e:
            print("Error during registration:", e)  # 🔥 Debug log
            return Response({"error": "Internal Server Error"}, status=500)

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
        try:
            # ✅ Delete the user's token on logout
            Token.objects.get(user=request.user).delete()
            return Response({"message": "Logged out successfully, token removed."}, status=200)
        except Token.DoesNotExist:
            return Response({"message": "No token found for user."}, status=400)

class UserProfileView(APIView):
    permission_classes = [AllowAny]
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request, username=None):
        try:
            if username:
                user = User.objects.get(username=username)
            elif request.user.is_authenticated:
                user = request.user
            else:
                return Response({"detail": "User not authenticated"}, status=400)

            profile = user.profile
            if request.user == user:  # Update last_seen only for self
                profile.last_seen = now()
                profile.save()

            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        

    def put(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            # 🔄 Also update User.email if provided
            new_email = request.data.get("email")
            if new_email:
                request.user.email = new_email
                request.user.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    


User = get_user_model()

class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []  # No authentication needed for GET, HEAD, OPTIONS
        return [permissions.IsAuthenticated()]  # Auth required for POST, PUT, DELETE

    def get_queryset(self):
        user_param = self.request.query_params.get('user')

        if user_param:
            try:
                user = User.objects.get(username=user_param)
                return Album.objects.filter(user=user)
            except User.DoesNotExist:
                return Album.objects.none()
        
        # 🛠️ Allow the authenticated user to manage their own albums
        if self.request.user.is_authenticated:
            return Album.objects.filter(user=self.request.user)
            
        # No user specified — show nothing. But in your frontend you need to specify the user you are viewing so it would show the album/images like this: /albums/?user=${username}
        return Album.objects.none()
        
        # ✅ Allow unauthenticated users to see all albums (or customize as needed). And when i say all i mean "ALL" users who are registered lol.
        # return Album.objects.all()

        # else:
        #     # Anonymous users get nothing if they don’t specify a user
        #     if self.request.user.is_authenticated:
        #         return Album.objects.filter(user=self.request.user)
        #     return Album.objects.none()

        # If you eventually want private albums, consider adding a public = models.BooleanField(default=True) to your Album model and change:
        # return Album.objects.filter(public=True)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlbumImageViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    # Only require authentication for modifying (POST/PUT/DELETE), not for viewing (GET)
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []  # No auth required for GET, HEAD, OPTIONS
        return [permissions.IsAuthenticated()]  # Auth required for POST, PUT, DELETE

    def get_queryset(self):
        album_id = self.request.query_params.get("album")
        queryset = AlbumImage.objects.all()  # Show all images to anyone
        if album_id:
            queryset = queryset.filter(album__id=album_id)
        return queryset

    def perform_create(self, serializer):
        album_id = self.request.data.get('album')
        album = Album.objects.get(id=album_id, user=self.request.user)
        serializer.save(album=album)
