from django.shortcuts import render, get_object_or_404
from games.models import Game

def game_records(request):
    custom_user = request.user.customuser
    games = Game.objects.filter(user=custom_user).order_by('created_at')
    return render(request, 'records/game_records.html', {'games': games})

def game_record_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'records/game_record_detail.html', {'game': game})
