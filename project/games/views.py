from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Game, Job, House
from accounts.models import CustomUser
from django.conf import settings

import random
import json
import os

def load_selection():
    path = os.path.join(settings.BASE_DIR, "games", "selection.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == "POST":
        custom_user = request.user.customuser

        game = Game.objects.create(
            user=custom_user,
            job=job,
            hospital_visited=random.randint(1, 4)
        )

        return redirect("games:select_house", game_id=game.id)

    return render(request, "games/job_detail.html", {"job": job})

@login_required
def select_job(request):
    selection_data = load_selection()
    jobs = selection_data.get('jobs', [])

    if request.method == 'POST':
        job_id = int(request.POST.get('job_id'))
        job = get_object_or_404(Job, id=job_id)
        
        return redirect('games:job_detail', job_id=job.id)

    return render(request, 'games/select_job.html', {'jobs': jobs})

@login_required
def select_house(request, game_id):
    selection_data = load_selection()
    houses = selection_data.get('houses', [])

    if request.method == 'POST':
        house_id = int(request.POST.get('house_id'))

        game = get_object_or_404(Game, id=game_id)

        if game.user != request.user.customuser:
            raise PermissionDenied("권한이 없습니다.")

        house = get_object_or_404(House, id=house_id)

        game.house = house
        game.save()

        return redirect('games:game_start', month=1, time=1)
    
    return render(request, 'games/select_house.html', {'houses': houses})

@login_required
def game_start(request, month, time):
    if month > 4:
        custom_user = request.user.customuser
        game = Game.objects.filter(user=custom_user, is_active=True).latest('created_at')
        return redirect('games:game_ending', game_id=game.id)
        
    selection_data = load_selection()
    custom_user = request.user.customuser
    game = Game.objects.filter(user=custom_user, is_active=True).latest('created_at')
    
    prev_month = game.current_month
    game.current_month = month
    game.is_morning = time

    if game.hospital_visited == month and time == 2:
        return redirect('games:hospital_event', game_id=game.id)

    if time == 1 and prev_month < month:
        game.current_money += game.job.salary
        game.current_money -= game.house.monthly_rent
        game.current_money -= (game.house.deposit)/4
        game.current_money = (int)(game.current_money)
        
        if game.current_money < 0:
            game.save()
            return redirect('games:game_fail', game_id=game.id)
    
    game.save()

    # 오전 일정
    if time == 1:
        if month == 3:
            if request.method == 'POST':
                return redirect('games:game_start', month=month, time=2)
            return render(request, 'games/festival.html', {'game': game})
            
        morning_dialogues = {
            1: [
                "씨 오늘도 파이팅!",
                "감사합니다.",
                "요새 주산지 왕버들 복원사업 추진한다 카던데 들었어요?",
                "들었죠. 왕버들 이식한다고 저수지까지 방류한대요.",
                "잘 됐으면 좋겠네요. 나중에 놀러가야겠다."
            ],
            2: [
                "씨 오늘 비 온다 카던데. 우산 챙겼나?",
                "아유 그럼요.",
                "내일 청송군 풋살연맹 취임식 있대요.",
                "대회도 한다던데. 가시나요?",
                "아, 당연히 가야죠! 창립기념 대회라던데."
            ],
            4: [
                "씨 주말 잘 보냈어?",
                "네! 내일도 주말이었으면 좋겠네요.",
                "다음주 화요일에 흰지팡이의 날인 거 아시죠?",
                "네, 청송문화예술회관 대공연장에서 만나겠네요.",
                "시각장애인 화합한마당이라니 기대되네요."
            ]
        }
        
        context = {
            'game': game,
            'dialogues': morning_dialogues.get(month, []),
            'user_nickname': custom_user.nickname
        }
        
        if request.method == 'POST':
            return redirect('games:game_start', month=month, time=2)
        
        return render(request, 'games/morning.html', context)
    
    # 오후 일정
    elif time == 2:
        if month == 3:
            if request.method == 'POST':
                return redirect('games:night_transition', month=month)
            return render(request, 'games/festival.html', {'game': game})

        if request.method == 'POST':
            if month == 1:
                restaurant_data = request.POST.get('restaurant')
                if isinstance(restaurant_data, str):
                    try:
                        restaurant_dict = json.loads(restaurant_data)
                        restaurant_name = restaurant_dict['name']
                    except (json.JSONDecodeError, KeyError):
                        restaurant_name = restaurant_data
                else:
                    restaurant_name = restaurant_data
        
                return redirect('games:restaurant_detail', 
                    game_id=game.id, 
                    restaurant_name=restaurant_name)
                
            elif month == 2:
                category = request.POST.get('category')
                places = [p for p in selection_data['places'] if p['category'] == category]
                game.save()
                return redirect('games:night_transition', month=month)
                
            elif month == 4:
                selected_ingredients = request.POST.getlist('ingredients')
                total_price = sum(
                    next(i['price'] for i in selection_data['cooking_ingredients'] if i['name'] == ingredient)
                    for ingredient in selected_ingredients
                )
                game.current_money -= total_price
                
                if game.current_money < 0:
                    game.save()
                    return redirect('games:game_fail', game_id=game.id)
                    
                game.save()
                
                cooking_result = get_cooking_result(selected_ingredients)
                context = {
                    'game': game,
                    'result': cooking_result,
                }
                return render(request, 'games/cooking_result.html', context)
            
            return redirect('games:night_transition', month=month)
            
        context = {
            'game': game,
            'month': month,
            'restaurants': selection_data['restaurants'] if month == 1 else None,
            'places': selection_data['places'] if month == 2 else None,
            'ingredients': selection_data['cooking_ingredients'] if month == 4 else None,
        }
        return render(request, 'games/afternoon.html', context)

@login_required
def night_transition(request, month):
    custom_user = request.user.customuser
    game = Game.objects.filter(user=custom_user, is_active=True).latest('created_at')
    
    if request.method == 'POST':
        next_month = month + 1
        return redirect('games:game_start', month=next_month, time=1)
        
    return render(request, 'games/night.html', {
        'game': game,
        'month': month
    })

@login_required
def hospital_event(request, game_id):
    selection_data = load_selection()
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        return redirect('games:hospital_visit', game_id=game.id)

    return render(request, 'games/hospital_event.html')

@login_required
def hospital_visit(request, game_id):
    selection_data = load_selection()
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        game.hospital_visited = 0
        game.save()
        return redirect('games:game_start', month=game.current_month+1, time=1)

    selected_hospital = random.choice(selection_data['hospitals'])
    game.current_money -= selected_hospital['price']
    game.save()
    
    return render(request, 'games/hospital.html', {'hospital': selected_hospital, 'game': game})

@login_required
def restaurant_detail(request, game_id, restaurant_name):
    selection_data = load_selection()
    game = get_object_or_404(Game, id=game_id)
    
    if game.user != request.user.customuser:
        raise PermissionDenied("권한이 없습니다.")
    
    selected_restaurant = next(
        (r for r in selection_data['restaurants'] if r['name'] == restaurant_name), 
        None
    )

    if selected_restaurant:
        game.current_money -= selected_restaurant['price']
        if game.current_money < 0:
            game.save()
            return redirect('games:game_fail', game_id=game.id)
    game.save()
    
    if request.method == 'POST':
        if game.hospital_visited == 1:
            return redirect('games:hospital_visit', game_id=game.id)
        return redirect('games:night_transition', month=1)
        
    context = {
        'game': game,
        'restaurant': selected_restaurant
    }
    
    return render(request, 'games/restaurant_detail.html', context)

def get_cooking_result(selected_ingredients):
    if set(selected_ingredients) == {"떡국떡"} or set(selected_ingredients) >= {"떡국떡", "곶감", "미꾸라지"}:
        return "떡국떡을 끓인 육수에 곶감을 넣어 단맛을 더하고 미꾸라지를 추가해서 깊은 맛을 냈습니다. 색다른 맛이네요!"
    elif set(selected_ingredients) >= {"곶감", "청송사과", "귤"}:
        return "곶감과 청송사과, 귤을 함께 잘라서 상큼한 샐러드를 만들었습니다. 신선하고 맛있네요!"
    elif set(selected_ingredients) >= {"청송사과", "오징어"} or set(selected_ingredients) == {"오징어"}:
        return "오징어 볶음 안에 청송사과를 넣어서 함께 볶았습니다. 달콤하고 짭조름한 맛이네요!"
    elif set(selected_ingredients) >= {"미꾸라지", "귤"}:
        return "미꾸라지를 깨끗하게 손질하고 귤즙과 함께 찜통에 쪄냈습니다. 상큼하고도 건강한 음식이네요!"
    else:
        return "사온 재료랑 집에 있는 음식까지 전부 섞어서 먹었습니다. 정말 맛있네요!"

@login_required
def cooking_result(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if game.user != request.user.customuser:
        raise PermissionDenied("권한이 없습니다.")
    
    if request.method == 'POST':
        if game.hospital_visited == 4:
            return redirect('games:hospital_visit', game_id=game.id)
        else:
            return redirect('games:game_ending', game_id=game.id)
    
    cooking_result = request.session.get('cooking_result', "요리 결과를 불러올 수 없습니다.")
    
    return render(request, 'games/cooking_result.html', {
        'game': game,
        'result': cooking_result
    })

@login_required
def game_ending(request, game_id):
    custom_user = request.user.customuser
    game = get_object_or_404(Game, id=game_id)
    game.is_active = False
    game.save()
    custom_user.play_count += 1
    custom_user.save()
    
    context = {
        'game': game,
        'region': '청송군',
        'custom_user': custom_user
    }
    return render(request, 'games/ending.html', context)

def game_fail(request, game_id):
    custom_user = request.user.customuser
    game = get_object_or_404(Game, id=game_id)
    game.is_active = False
    game.save()
    
    context = {
        'game': game,
        'custom_user': custom_user
    }

    return render(request, 'games/fail.html', context)