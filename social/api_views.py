from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from social.models import Post
from social.serializers import (
    CommentSerializer,
    PostSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({"message": "Conta criada com sucesso!", "username": user.username}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"message": "Login realizado!", "username": user.username})
    return Response({"detail": "Usuário ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return Response({"message": "Sessão encerrada."})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def profile_api(request):
    user = request.user
    profile = user.profile

    if request.method == "GET":
        following_users = User.objects.filter(profile__in=profile.following.all())
        followers_users = User.objects.filter(profile__in=profile.followers.all())
        return Response({
            "user": UserPublicSerializer(user, context={"request": request}).data,
            "following": UserPublicSerializer(following_users, many=True, context={"request": request}).data,
            "followers": UserPublicSerializer(followers_users, many=True, context={"request": request}).data,
        })

    first_name = request.data.get("first_name")
    bio = request.data.get("bio")
    password = request.data.get("password")
    avatar = request.FILES.get("avatar")

    if first_name is not None and first_name != "":
        user.first_name = first_name
    if password is not None and password != "":
        user.set_password(password)
        user.save()
        update_session_auth_hash(request, user)
    else:
        user.save()

    if bio is not None:
        profile.bio = bio
    if avatar is not None:
        profile.avatar = avatar
    profile.save()

    return Response({
        "message": "Perfil atualizado com sucesso!",
        "user": UserPublicSerializer(user, context={"request": request}).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_list_api(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.exclude(id=request.user.id).order_by("username")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query))
    serializer = UserPublicSerializer(users, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_follow_api(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return Response({"detail": "Você não pode seguir a si mesmo."}, status=status.HTTP_400_BAD_REQUEST)

    my_profile = request.user.profile
    target_profile = target_user.profile

    if my_profile.following.filter(id=target_profile.id).exists():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True

    return Response({
        "following": following,
        "followers_count": target_profile.followers.count(),
    })


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_profiles = self.request.user.profile.following.all()
        following_users = User.objects.filter(profile__in=following_profiles)
        return Post.objects.filter(
            Q(author__in=following_users) | Q(author=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({"detail": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return Response({"liked": liked, "likes_count": post.likes.count()})

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
