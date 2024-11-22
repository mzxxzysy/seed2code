from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from accounts.forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import CustomUser
from django.contrib import messages

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
    
    # if not form.is_valid():
    #     print(form.errors)
    # return render(request, 'accounts/signup.html', {'form': form})
    
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    
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
                messages.error(request, "존재하지 않는 아이디 혹은 잘못된 비밀번호입니다.")
        else:
            # form.is_valid()가 False일 때 메시지 추가
            messages.error(request, "아이디와 비밀번호를 다시 확인해주세요.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')