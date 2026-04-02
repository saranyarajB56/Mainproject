from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile, Comment, Message

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "video"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'cover_image', 'status', 'occupation', 'location', 'website']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["receiver", "text"]

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        error_messages = {
            'username': {
                'invalid': "Usernames can’t contain spaces. Try underscores (_) or dots (.) instead."
            }
        }

# class MessageForm(forms.ModelForm):
#     class Meta:
#         model = Message
#         fields = ["text"]   # only the text field for sending
#         widgets = {
#             "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Type your message..."})
#         }
class MessageForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Receiver",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Message
        fields = ["receiver", "text"]


