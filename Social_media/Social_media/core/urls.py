from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("user-dashboard/", views.feed_view, name="user_dashboard"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("feed/", views.feed_view, name="feed"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    path("comment/<int:post_id>/", views.comment_post, name="comment_post"),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path("user_messages/", views.messages_view, name="user_messages"),
    path('user_settings/', views.user_settings_view, name='user_settings'),
    path("search/", views.user_search, name="user_search"),
    path("profile/guest/<str:username>/", views.profile_details_guest, name="profile_details_guest"),
    # path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("conversation/<int:user_id>/", views.conversation_view, name="conversation"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("users/", views.users_list, name="users_list"),
    path("posts/", views.posts_list, name="posts_list"), 
    path("likes/", views.likes_list, name="likes_list"),
    path("comments/", views.comments_list, name="comments_list"),  # ✅ add this
    path("messages/", views.messages_list, name="messages_list"),
    path("followers/", views.followers_list, name="followers_list"),
    path("admin_settings/", views.admin_settings, name="admin_settings"),
    path("followers/<str:username>/", views.followers_page, name="followers_page"),
    path('forgot-password/', views.forgot_password_view, name='forgotpassword'),
    path("reset-password/", views.reset_password_view, name="resetpassword"),
    path("stories/", views.user_stories, name="user_stories"),

]












