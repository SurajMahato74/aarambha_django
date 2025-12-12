from django.db import models

class Branch(models.Model):
    code = models.CharField(max_length=10, unique=True, default='TEMP')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, default='Not specified')
    admin = models.ForeignKey('users.CustomUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_branch')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']