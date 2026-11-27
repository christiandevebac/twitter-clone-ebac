from django.contrib.auth.models import User
from rest_framework import serializers
from social.models import Comment, Post, Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data.get("first_name", ""),
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    bio = serializers.CharField(source="profile.bio", read_only=True)
    followers_count = serializers.IntegerField(source="profile.followers.count", read_only=True)
    following_count = serializers.IntegerField(source="profile.following.count", read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "avatar",
            "bio",
            "followers_count",
            "following_count",
            "is_following",
        ]

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user.profile.following.filter(id=obj.profile.id).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_name = serializers.CharField(source="author.first_name", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author_username", "author_name", "content", "created_at"]
        read_only_fields = ["id", "author_username", "author_name", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "likes_count",
            "is_liked",
            "comments",
            "created_at",
        ]
        read_only_fields = ["id", "author", "likes_count", "is_liked", "comments", "created_at"]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
