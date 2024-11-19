from django.db import models
from django.contrib.auth.models import User

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    play_count = models.IntegerField(default=0)
    last_region = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.CharField(max_length=100, default='img/홈페이지일러.png')

    def __str__(self):
        return f"{self.user.username}"