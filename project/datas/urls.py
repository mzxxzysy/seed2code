from django.urls import path
from . import views

app_name = 'datas'
urlpatterns = [
    path('', views.data_list, name='list'),
    path('<str:region_name>/', views.region_detail, name='region_detail'),
    path('<str:region_name>/tour/', views.tour_detail, name='tour_detail'),
]
