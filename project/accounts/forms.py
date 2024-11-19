from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    nickname = forms.CharField(
        label="Nick name",
        max_length=20,
    )
    username = forms.CharField(
        label="ID",
        min_length=5,
        max_length=20,
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=8,
        max_length=20,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        min_length=8,
        max_length=20,
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("중복 아이디가 있습니다.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not any(char.isalpha() for char in password1) or not any(char.isdigit() for char in password1):
            raise ValidationError("비밀번호에는 문자와 숫자가 모두 포함되어야 합니다.")
        if not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>/?`~' for char in password1):
            raise ValidationError("비밀번호에는 최소 하나의 특수문자가 포함되어야 합니다.")
        if len(password1) > 20:
            raise ValidationError("비밀번호는 20자를 초과할 수 없습니다.")
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("비밀번호 비일치. 다시 입력해 주세요.")
        return password2