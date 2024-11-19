from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from accounts.forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import CustomUser

def signup_view(request):
    if request.method == "GET":
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})
    
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        # CustomUser 생성
        CustomUser.objects.create(
            user=user,
            nickname=form.cleaned_data['nickname'],
            play_count=0,
            last_region=None
        )
        return redirect('accounts:login')
    return render(request, 'accounts/signup.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:main')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')