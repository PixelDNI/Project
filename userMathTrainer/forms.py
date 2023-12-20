from django.contrib.auth import forms
from django.forms import Form
from django import forms as f
from adminMathTrainer.models import User, UserProfile
from django.forms import ModelForm
from adminMathTrainer.models import Comment



class UserCreationForm(forms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form_input'
        self.fields['email'].widget.attrs['class'] = 'form_input'

    class Meta:
        model = User
        fields = ('username', 'email',)


class AuthorCreationForm(forms.UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email',)


class SearchForm(Form):
    searched = f.CharField(label='Search', max_length=100)
    is_free = f.BooleanField(label='Free', required=False)


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text_field',)

class UpdateUserProfile(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_photo',)