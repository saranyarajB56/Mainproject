from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg')
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    status = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    followers = models.ManyToManyField(User, related_name="profile_followers", blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.content[:30] if self.content else f"Post by {self.author.username}"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # single timestamp field

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.text[:20]}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "follower")  # prevents duplicate follows

    def __str__(self):
        return f"{self.follower.username} follows {self.user.username}"
    
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="My Site")
    admin_email = models.EmailField(default="admin@example.com")
    admin_name = models.CharField(max_length=100, default="Admin")
    admin_phone = models.CharField(max_length=20, blank=True, null=True)
    maintenance_mode = models.CharField(
        max_length=10,
        choices=[("on", "On"), ("off", "Off")],
        default="off"
    )
    maintenance_message = models.TextField(blank=True, null=True)
    maintenance_schedule = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.site_name
