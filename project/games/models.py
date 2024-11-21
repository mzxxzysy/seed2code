from django.db import models
from accounts.models import CustomUser

class Job(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    salary = models.IntegerField()
    profile_image = models.CharField(max_length=100, null=True, blank=True)

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
    job = models.ForeignKey(Job, on_delete=models.CASCADE) # 직장
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True) # 집
    created_at = models.DateTimeField(auto_now_add=True) # 시작 시기
    is_active = models.BooleanField(default=True) # 게임 활성화
    current_money = models.IntegerField(default=50) # 자산
    current_month = models.IntegerField(default=1) # 달
    is_morning = models.IntegerField(default=1) # 1=오전, 2=오후
    hospital_visited = models.IntegerField(null=True, blank=True) # 병원 방문 달

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Game {self.id} - {self.user.nickname}"