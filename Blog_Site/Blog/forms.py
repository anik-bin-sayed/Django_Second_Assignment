from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment, Category
from django.contrib.auth.forms import UserCreationForm

from ckeditor.widgets import CKEditorWidget

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content' : forms.Textarea(attrs={'row':1,'col':4, 'placeholder': "Write your comment..."})
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'feature_image', 'tags', 'category', 'status']
        widgets = {
            'content': CKEditorWidget(),  
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email','password1', 'password2']