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
            hospital_visited=random.randint(3, 4)
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

    if game.hospital_visited == month and time == 3:  
        return redirect('games:hospital_event', game_id=game.id)

    # 월간 정산
    if time == 1 and prev_month < month:
        game.current_money += game.job.salary
        game.current_money -= game.house.monthly_rent
        game.current_money -= (game.house.deposit)/12
        game.current_money = int(game.current_money)
        
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
        
        if request.method == 'POST':
            return redirect('games:game_start', month=month, time=2)
        
        return render(request, 'games/morning.html', { 'game': game })
    
    # 오후 일정
    elif time == 2:
        if month == 3:
            if request.method == 'POST':
                return redirect('games:game_start', month=month, time=3)
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
                if request.method == 'POST':
                    category = request.POST.get('category')
                    if category:  # 선택된 카테고리 처리
                        return redirect('games:place_detail', game_id=game.id, category=category)
                
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
                
                cooking_result = get_cooking_result(selected_ingredients)     
                game.cooked_food = cooking_result['result']  # 만든 음식 저장
                game.save()
                context = {
                    'game': game,
                    'result': cooking_result,
                }
                return render(request, 'games/cooking_result.html', context)
            
            return redirect('games:game_start', month=month, time=3)  # 오후 일정 완료 후 병원 체크
        context = {
            'game': game,
            'month': month,
            'restaurants': selection_data['restaurants'] if month == 1 else None,
            'places': selection_data['places'] if month == 2 else None,
            'ingredients': selection_data['cooking_ingredients'] if month == 4 else None,
        }
        return render(request, 'games/afternoon.html', context)

    elif time == 3:
        if request.method == 'POST':
            if game.hospital_visited == month:
                return redirect('games:hospital_event', game_id=game.id)
            return redirect('games:night_transition', month=month)
        
        return render(request, 'games/night.html', {
            'game': game,
            'month': month
        })

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
        game.visited_restaurant = selected_restaurant.get('menu', '알 수 없음')
        game.save()
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

@login_required
def place_detail(request, game_id, category):
    selection_data = load_selection()
    game = get_object_or_404(Game, id=game_id)
    places = [p for p in selection_data['places'] if p['category'] == category]
    
    if not places:
        return redirect('games:night_transition', month=2)

    selected_place = random.choice(places)
    game.visited_place = selected_place.get('name', '알 수 없음')
    game.save()
    
    if request.method == 'POST':
        return redirect('games:night_transition', month=2)
    
    return render(request, 'games/place_detail.html', {'place': selected_place, 'game_id': game_id})

def get_cooking_result(selected_ingredients):
    if set(selected_ingredients) == {"떡국떡"} or set(selected_ingredients) >= {"떡국떡", "곶감", "미꾸라지"}:
        result = "떡국"
        description = "떡국떡을 끓인 육수에 곶감을 넣어 단맛을 더하고 미꾸라지를 추가해서 깊은 맛을 냈습니다. 색다른 맛이네요!"
        cook_img = "img/tteok.png"
        context = { "result": result, "description": description, "cook_img": cook_img }
        return context
    elif set(selected_ingredients) >= {"곶감", "청송사과", "귤"}:
        result = "샐러드"
        description = "곶감과 청송사과, 귤을 함께 잘라서 상큼한 샐러드를 만들었습니다. 신선하고 맛있네요!"
        cook_img = "img/salad.png"
        context = { "result": result, "description": description, "cook_img": cook_img }
        return context
    elif set(selected_ingredients) >= {"청송사과", "오징어"} or set(selected_ingredients) == {"오징어"}:
        result = "오징어 볶음"
        description = "오징어 볶음 안에 청송사과를 넣어서 함께 볶았습니다. 달콤하고 짭조름한 맛이네요!"
        cook_img = "img/squid.png"
        context = { "result": result, "description": description, "cook_img": cook_img }
        return context
    elif set(selected_ingredients) >= {"미꾸라지", "귤"}:
        result = "미꾸라지 찜"
        description = "미꾸라지를 깨끗하게 손질하고 귤즙과 함께 찜통에 쪄냈습니다. 상큼하고도 건강한 음식이네요!"
        cook_img = "img/zzim.png"
        context = { "result": result, "description": description, "cook_img": cook_img }
        return context
    else:
        result = "전부 섞어 먹는 음식"
        description = "사온 재료랑 집에 있는 음식까지 전부 섞어서 먹었습니다. 정말 맛있네요!"
        cook_img = "img/every.png"
        context = { "result": result, "description": description, "cook_img": cook_img }
        return context

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
    custom_user.play_count += 1
    custom_user.save()
    game.play_count = custom_user.play_count
    game.save()
    
    context = {
        'game': game,
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