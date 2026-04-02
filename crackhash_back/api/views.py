from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Task, TaskSerializer

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    def create(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        task = Task.objects.get(id=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk=None):
        task = Task.objects.get(id=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        task = Task.objects.get(id=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)