from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name