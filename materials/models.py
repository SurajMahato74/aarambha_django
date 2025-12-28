from django.db import models
from django.contrib.auth import get_user_model
from branches.models import Branch

User = get_user_model()

class MaterialCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Material Categories"

class ReadingMaterial(models.Model):
    ASSIGNMENT_CHOICES = [
        ('all', 'All Users'),
        ('individual', 'Individual Users'),
        ('branch', 'By Branch'),
        ('branch_individual', 'Branch + Individual'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reading_materials/')
    cover_image = models.ImageField(upload_to='reading_materials/covers/', blank=True, null=True)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_CHOICES, default='all')
    assigned_users = models.ManyToManyField(User, blank=True)
    assigned_branches = models.ManyToManyField(Branch, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_materials')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']