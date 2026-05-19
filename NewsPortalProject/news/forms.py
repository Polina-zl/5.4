from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Заголовок должен быть длиннее 5 символов')
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 20:
            raise forms.ValidationError('Текст должен быть длиннее 20 символов')
        return text


class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get_or_create(name='common')[0]
        common_group.user_set.add(user)
        return user