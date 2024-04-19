from django.contrib.auth.models import User
from django.db import models

class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')

    def __str__(self):
        return self.image.url

class PHAnalysis(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    ph_value = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
