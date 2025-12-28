from django.db import models
from .models import Task

class TaskMaterial(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='task_materials/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task.title} - {self.filename}"