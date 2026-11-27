from django.urls import include, path
from rest_framework.routers import DefaultRouter
from social import api_views, views

router = DefaultRouter()
router.register(r"posts", api_views.PostViewSet, basename="post")

urlpatterns = [
    path("", views.feed_page, name="feed"),
    path("login/", views.login_page, name="login"),
    path("api/register/", api_views.register_api, name="api_register"),
    path("api/login/", api_views.login_api, name="api_login"),
    path("api/logout/", api_views.logout_api, name="api_logout"),
    path("api/profile/", api_views.profile_api, name="api_profile"),
    path("api/users/", api_views.users_list_api, name="api_users"),
    path("api/users/<int:user_id>/follow/", api_views.toggle_follow_api, name="api_follow"),
    path("api/", include(router.urls)),
]
