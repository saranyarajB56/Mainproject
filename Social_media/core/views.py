from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Post, Profile,  Comment, Message
from .forms import SignupForm, PostForm, ProfileForm, CommentForm, MessageForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Post, Profile, Comment, Message, ContactMessage
from .forms import SignupForm, PostForm, ProfileForm, CommentForm, MessageForm,UsernameChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from core.models import Profile, Post, Like, Comment, Message, Follower, Activity, SiteSettings
from django.contrib.auth.hashers import make_password



# ----------------signup--------------------
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # Save and get the new user
            user = form.save()

            # Record the signup activity
            Activity.objects.create(user=user, action="Signed up")

            # Optionally log the user in right away
            login(request, user)

            # Redirect after signup
            return redirect("feed")  
        else:
            return render(
                request,
                "core/signup.html",
                {"form": form, "error": "Invalid details"}
            )
    else:
        form = SignupForm()
    return render(request, "core/signup.html", {"form": form})

# forgot password-----------------
def forgot_password_view(request):
    return render(request, 'core/forgot_password.html')

# reset password-------------------
def reset_password_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "core/forgot_password.html")

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()

            # Authenticate with the new password
            user = authenticate(request, username=username, password=new_password)
            if user is not None:
                login(request, user)   # attach user to session
                messages.success(request, "Password reset successful! You are now logged in.")
                return redirect("home")  # change to your dashboard/home route
            else:
                messages.error(request, "Authentication failed after reset.")
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, "core/forgot_password.html")

# --------login-----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.is_superuser or user.is_staff:
                Activity.objects.create(user=request.user, action="Admin loggedin")

                return redirect("admin_dashboard")
            else:
                Activity.objects.create(user=request.user, action="User loggedin")

                return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "core/login.html")

@login_required
def admin_dashboard(request):
    return render(request, "core/admin_dashboard.html")

@login_required
def user_dashboard(request):
    return render(request, "core/feed.html")


# logout-----------
def logout_view(request):
    if request.user.is_authenticated:
        Activity.objects.create(user=request.user, action="Logged Out")
    logout(request)
    return redirect("login")

# ----------feed----------
@login_required
def feed_view(request):
    posts = Post.objects.all().order_by("-created_at")
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Activity.objects.create(user=request.user, action="Created a post")
            return redirect("feed")
    else:
        form = PostForm()
    return render(request, "core/feed.html", {"posts": posts, "form": form})

# profile_view----------
def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    posts = Post.objects.filter(author=profile.user)
    followers_count = profile.followers.count()  # ✅ calculate here

    context = {
        "profile": profile,
        "posts": posts,
        "followers_count": followers_count,
    }
    return render(request, "core/profile.html", context)


# edit profile----------
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # ✅ include request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            Activity.objects.create(user=request.user, action="Profile Edited")
            return redirect("profile_detail", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "core/edit_profile.html", {"form": form})

# profile details-------------
@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)

    # ✅ Fetch posts authored by this user
    posts = Post.objects.filter(author=user).order_by("-created_at")

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', username=user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        'core/profile.html',
        {
            'profile': profile,
            'form': form,
            'posts': posts,   # ✅ pass posts to template
        }
    )

# profile details guest--------------
@login_required
def profile_details_guest(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    is_following = Follower.objects.filter(user=user, follower=request.user).exists()
    followers_count = Follower.objects.filter(user=user).count()
    
    posts = Post.objects.filter(author=user).order_by('-created_at')

    context = {
        "profile": profile,
        "is_following": is_following,
        "followers_count": followers_count,
        "posts": posts,  
    }
    return render(request, "core/profile_details_guest.html", context)

# like------------
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post)

    if like.exists():
        like.delete()   # Unlike
        Activity.objects.create(user=request.user, action="Unlike a post")
    else:
        Like.objects.create(user=request.user, post=post)  # Like
        Activity.objects.create(user=request.user, action="Like a post")

    return redirect('feed')

# comment---------
@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
            Activity.objects.create(user=request.user, action="Commented a post")
    return redirect('feed')

# delete-------------------
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author == request.user:  # Only allow author to delete
        comment.delete()
        Activity.objects.create(user=request.user, action="Deleted a Comment")
    return redirect('feed')

# message-----------------
@login_required
def messages_view(request):
    # inbox = Message.objects.filter(receiver=request.user)
    # if request.method == "POST":
    #     form = MessageForm(request.POST)
    #     if form.is_valid():
    #         msg = form.save(commit=False)
    #         msg.sender = request.user
    #         msg.save()
    #         messages.success(request, "Message sent successfully!")
    #         Activity.objects.create(user=request.user, action="Sent a Message")
    #         return redirect("messages")
    # else:
    #     form = MessageForm()
    # return render(request, "core/user_messages.html", {"inbox": inbox, "form": form})
    inbox = Message.objects.filter(receiver=request.user).order_by("-created_at")  # use created_at
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            messages.success(request, "Message sent successfully!")  
            return redirect("user_messages")
    else:
        form = MessageForm()
        # exclude self from receiver dropdown
        form.fields["receiver"].queryset = User.objects.exclude(id=request.user.id)

    return render(request, "core/user_messages.html", {"inbox": inbox, "form": form})




# settings--------------
@login_required
def user_settings_view(request):
    if request.method == 'POST':
        username_form = UsernameChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if 'username_submit' in request.POST:
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Username updated successfully!")
                Activity.objects.create(user=request.user, action="Username Updated")
                return redirect('user_settings')
            else:
                messages.error(request, "Please correct the errors in the username form.")

        elif 'password_submit' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # keeps user logged in
                messages.success(request, "Password changed successfully!")
                Activity.objects.create(user=request.user, action="Password Updated")
                return redirect('user_settings')
            else:
                messages.error(request, "Please correct the errors in the password form.")
    else:
        username_form = UsernameChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'core/settings.html', {
    'username_form': username_form,
    'password_form': password_form
})

# search user-----------------
def user_search(request):
    query = request.GET.get("q")
    results = []
    if query:
        results = User.objects.filter(username__icontains=query)
    return render(request, "core/user_search.html", {"results": results, "query": query})

# follow user-------------
@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    follow = Follower.objects.filter(user=target_user, follower=request.user)

    if follow.exists():
        follow.delete()
        Activity.objects.create(user=request.user, action=f"Unfollowed {target_user.username}")
    else:
        Follower.objects.create(user=target_user, follower=request.user)
        Activity.objects.create(user=request.user, action=f"Followed {target_user.username}")

    return redirect("profile_details_guest", username=target_user.username)



# about-------
def about_view(request):
    return render(request, "core/about.html")

# contact------------
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        ContactMessage.objects.create(name=name, email=email, message=message)
        return render(request, "core/contact.html", {"success": True})

    return render(request, "core/contact.html")

# privacy-----------------
def privacy_view(request):
    return render(request, "core/privacy.html")

# chat---------
# def conversation_view(request, user_id):
#     other_user = get_object_or_404(User, id=user_id)

#     # Get all messages between the logged-in user and the other user
#     messages = Message.objects.filter(
#         sender__in=[request.user, other_user],
#         receiver__in=[request.user, other_user]
#     ).order_by("created_at")   # ✅ use created_at instead of timestamp

#     # Handle sending new message
#     if request.method == "POST":
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             new_msg = form.save(commit=False)
#             new_msg.sender = request.user
#             new_msg.receiver = other_user
#             new_msg.save()
#             return redirect("conversation", user_id=user_id)
#     else:
#         form = MessageForm()

#     return render(request, "core/conversation.html", {
#         "conversation": messages,
#         "other_user": other_user,
#         "form": form,
#     })
def conversation_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Get all messages exchanged between the logged-in user and the other user
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("created_at")   # ✅ use created_at consistently

    # Handle sending new message
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            new_msg = form.save(commit=False)
            new_msg.sender = request.user
            new_msg.receiver = other_user   # ✅ always set receiver explicitly
            new_msg.save()
            return redirect("conversation", user_id=user_id)
    else:
        form = MessageForm()

    return render(request, "core/conversation.html", {
        "conversation": messages,
        "other_user": other_user,
        "form": form,
    })


# inbox------------

def inbox_view(request):
    # All messages received by the logged-in user
    received_messages = Message.objects.filter(receiver=request.user)

    # Get distinct senders
    senders = received_messages.values_list("sender", flat=True).distinct()

    # Build inbox list with latest message per sender
    inbox = []
    for sender_id in senders:
        latest_msg = received_messages.filter(sender_id=sender_id).order_by("-timestamp").first()
        inbox.append(latest_msg)

    return render(request, "core/messages.html", {
        "inbox": inbox,
    })

# delete post--------------
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        Activity.objects.create(user=request.user, action="Deleted a post")
        return redirect("profile", username=request.user.username)  
    return redirect("profile", username=request.user.username)

def admin_dashboard(request):
    context = {
        "users_count": User.objects.count(),
        "posts_count": Post.objects.count(),
        "likes_count": Like.objects.count(),   # clean and direct
        "comments_count": Comment.objects.count(),
        "messages_count": Message.objects.count(),
        "followers_count": Follower.objects.count(),
        "recent_activities_count": Activity.objects.count(),
        "recent_activities": Activity.objects.order_by("-created_at")[:10],
    }
    return render(request, "core/admin_dashboard.html", context)

def users_list(request):
    users = User.objects.all()
    return render(request, "core/users_list.html", {"users": users})

def posts_list(request):
    # posts = Post.objects.all()
    posts = Post.objects.select_related('author').all()
    return render(request, "core/posts_list.html", {"posts": posts})

def likes_list(request):
    likes = Like.objects.all()
    return render(request, "core/likes_list.html", {"likes": likes})

def comments_list(request):
    comments = Comment.objects.all()
    return render(request, "core/comments_list.html", {"comments": comments})

def messages_list(request):
    messages = Message.objects.all()
    return render(request, "core/messages_list.html", {"messages": messages})

def followers_list(request):
    followers = Follower.objects.all()
    return render(request, "core/followers_list.html", {"followers": followers})

def admin_settings_view(request):
    return render(request, "core/admin_settings.html")

@login_required
def followers_page(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follower.objects.filter(user=user).select_related("follower")

    return render(request, "core/followers_page.html", {
        "profile_user": user,
        "followers": followers,
    })

@login_required
def followers_page(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follower.objects.filter(user=user).select_related("follower")
    followers_count = followers.count()   # 👈 count followers

    return render(request, "core/followers_page.html", {
        "profile_user": user,
        "followers": followers,
        "followers_count": followers_count,   # 👈 pass to template
    })

def admin_settings(request):
    settings, created = SiteSettings.objects.get_or_create(id=1)  # one record only
    if request.method == "POST":
        settings.site_name = request.POST.get("site_name")
        settings.admin_email = request.POST.get("admin_email")
        settings.admin_name = request.POST.get("admin_name")
        settings.admin_phone = request.POST.get("admin_phone")
        settings.maintenance_mode = request.POST.get("maintenance_mode")
        settings.maintenance_message = request.POST.get("maintenance_message")
        settings.maintenance_schedule = request.POST.get("maintenance_schedule")
        settings.save()

        messages.success(request, "Settings updated successfully!")
        return redirect("admin_settings.html")

    return render(request, "core/admin_settings.html", {
        "site_name": settings.site_name,
        "admin_email": settings.admin_email,
        "admin_name": settings.admin_name,
        "admin_phone": settings.admin_phone,
        "maintenance_mode": settings.maintenance_mode,
        "maintenance_message": settings.maintenance_message,
        "maintenance_schedule": settings.maintenance_schedule,
    })

def user_stories(request):
    return render(request, "core/user_stories.html")
