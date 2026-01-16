from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'extra_details', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'content': forms.Textarea(attrs={'class': 'border rounded p-2 w-full', 'rows': 5}),
            'extra_details': forms.Textarea(attrs={'class': 'border rounded p-2 w-full', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'image': forms.FileInput(attrs={'class': 'border rounded p-2 w-full'}),
        }