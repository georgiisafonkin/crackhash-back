from django.db import models
from rest_framework import serializers

# Create your models here.

class Task(models.Model):
    hash = models.CharField(max_length=32)
    maxLength = models.IntegerField()
    status = models.CharField(max_length=20)
    result = models.JSONField(default=list, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    finishedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hash


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'