from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('job/', views.select_job, name='select_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('house/<int:game_id>/', views.select_house, name='select_house'),
    path('<int:month>/<int:time>/', views.game_start, name='game_start'),
    path('night/<int:month>/', views.night_transition, name='night_transition'),
    path('restaurant_detail/<int:game_id>/<str:restaurant_name>/', views.restaurant_detail, name='restaurant_detail'),
    path('hospital_event/<int:game_id>/', views.hospital_event, name='hospital_event'),
    path('hospital/<int:game_id>/', views.hospital_visit, name='hospital_visit'),
    path('cooking-result/<int:game_id>/', views.cooking_result, name='cooking_result'),
    path('<int:game_id>/', views.game_ending, name='game_ending'),
    path('fail/<int:game_id>/', views.game_fail, name="game_fail"),
]