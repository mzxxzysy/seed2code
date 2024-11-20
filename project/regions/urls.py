from django.urls import path
from .views import *

app_name = 'regions'
urlpatterns = [
    path('test/<int:question_number>/', test, name='test'),
]
