from django.urls import path
from . import views

app_name = 'records'
urlpatterns = [
    path('', views.game_records, name='list'),
    path('<int:game_id>/', views.game_record_detail, name='record_detail'),

]