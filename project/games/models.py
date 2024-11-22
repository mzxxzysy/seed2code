from django.db import models
from accounts.models import CustomUser
from regions.models import Region

class Job(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    salary = models.IntegerField()
    profile_image = models.CharField(max_length=100, null=True, blank=True)
    work_image = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class House(models.Model):
    name = models.CharField(max_length=100)
    deposit = models.IntegerField()
    monthly_rent = models.IntegerField()
    image = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='games') # 유저
    region = models.CharField(max_length=255, default="경상북도 청송군")
    job = models.ForeignKey(Job, on_delete=models.CASCADE) # 직장
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True) # 집
    created_at = models.DateTimeField(auto_now_add=True) # 시작 시기
    is_active = models.BooleanField(default=True) # 게임 활성화
    current_money = models.IntegerField(default=50) # 자산
    current_month = models.IntegerField(default=1) # 달
    is_morning = models.IntegerField(default=1) # 1=오전, 2=오후
    hospital_visited = models.IntegerField(null=True, blank=True) # 병원 방문 달
    visited_restaurant = models.CharField(max_length=255, null=True, blank=True) # 방문한 맛집
    cooked_food = models.CharField(max_length=255, null=True, blank=True) # 만든 음식
    visited_place = models.CharField(max_length=255, null=True, blank=True) # 놀러간 곳
    play_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Game {self.id} - {self.user.nickname}"