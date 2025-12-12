from django.db import models
# tasks/models.py
class Task(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    assigned_to = models.ManyToManyField('users.CustomUser', related_name='assigned_tasks')
    assigned_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='created_tasks')
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    proof_file = models.FileField(upload_to='task_proofs/', blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)