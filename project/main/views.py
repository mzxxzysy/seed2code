from django.shortcuts import render
from accounts.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist

def main(request):
    user = request.user
    if user.is_authenticated:
        try:
            custom_user = CustomUser.objects.get(user=user)
        except ObjectDoesNotExist:
            custom_user = CustomUser.objects.create(
                user=user,
                nickname=user.username,
                play_count=0,
                last_region=None
            )
    else:
        custom_user = None

    next_play = custom_user.play_count + 1

    return render(request, 'main/main.html', {'user': user, 'custom_user': custom_user, 'next_play': next_play })