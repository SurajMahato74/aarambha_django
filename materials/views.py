from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ReadingMaterial, MaterialCategory
from branches.models import Branch

User = get_user_model()

class MyMaterialsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_branch = getattr(user, 'branch', None)
        
        materials = ReadingMaterial.objects.filter(is_active=True)
        
        # Filter based on assignment
        user_materials = materials.filter(
            Q(assignment_type='all') |
            Q(assignment_type='individual', assigned_users=user) |
            Q(assignment_type='branch', assigned_branches=user_branch) |
            Q(assignment_type='branch_individual', assigned_branches=user_branch) |
            Q(assignment_type='branch_individual', assigned_users=user)
        ).distinct()

        data = []
        for material in user_materials:
            data.append({
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'category': material.category.name,
                'file_url': material.file.url if material.file else None,
                'cover_image_url': material.cover_image.url if material.cover_image else None,
                'created_at': material.created_at.isoformat(),
            })

        return Response({'materials': data})

class AdminMaterialsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        materials = ReadingMaterial.objects.all()
        data = []
        for material in materials:
            assigned_users = [{'id': u.id, 'name': f"{u.first_name} {u.last_name}"} for u in material.assigned_users.all()]
            assigned_branches = [{'id': b.id, 'name': b.name} for b in material.assigned_branches.all()]
            
            data.append({
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'category': {'id': material.category.id, 'name': material.category.name},
                'file_url': material.file.url if material.file else None,
                'cover_image_url': material.cover_image.url if material.cover_image else None,
                'assignment_type': material.assignment_type,
                'assigned_users': assigned_users,
                'assigned_branches': assigned_branches,
                'is_active': material.is_active,
                'created_at': material.created_at.isoformat(),
            })

        return Response({'materials': data})

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            category = MaterialCategory.objects.get(id=request.data.get('category_id'))
            
            material = ReadingMaterial.objects.create(
                title=request.data.get('title'),
                description=request.data.get('description'),
                category=category,
                file=request.FILES.get('file'),
                cover_image=request.FILES.get('cover_image'),
                assignment_type=request.data.get('assignment_type', 'all'),
                created_by=request.user
            )

            # Handle assignments
            if material.assignment_type in ['individual', 'branch_individual']:
                user_ids = request.data.getlist('assigned_users[]')
                if user_ids:
                    material.assigned_users.set(User.objects.filter(id__in=user_ids))

            if material.assignment_type in ['branch', 'branch_individual']:
                branch_ids = request.data.getlist('assigned_branches[]')
                if branch_ids:
                    material.assigned_branches.set(Branch.objects.filter(id__in=branch_ids))

            return Response({'message': 'Material created successfully'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            material = ReadingMaterial.objects.get(id=pk)
            
            if request.data.get('title'):
                material.title = request.data.get('title')
            if request.data.get('description'):
                material.description = request.data.get('description')
            if request.data.get('category_id'):
                material.category = MaterialCategory.objects.get(id=request.data.get('category_id'))
            if request.FILES.get('file'):
                material.file = request.FILES.get('file')
            if request.FILES.get('cover_image'):
                material.cover_image = request.FILES.get('cover_image')
            if request.data.get('assignment_type'):
                material.assignment_type = request.data.get('assignment_type')
            
            material.save()
            
            # Handle assignments
            if material.assignment_type in ['individual', 'branch_individual']:
                user_ids = request.data.getlist('assigned_users[]')
                if user_ids:
                    material.assigned_users.set(User.objects.filter(id__in=user_ids))
                else:
                    material.assigned_users.clear()

            if material.assignment_type in ['branch', 'branch_individual']:
                branch_ids = request.data.getlist('assigned_branches[]')
                if branch_ids:
                    material.assigned_branches.set(Branch.objects.filter(id__in=branch_ids))
                else:
                    material.assigned_branches.clear()

            return Response({'message': 'Material updated successfully'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MaterialCategoriesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = MaterialCategory.objects.filter(is_active=True)
        data = [{'id': c.id, 'name': c.name, 'description': c.description} for c in categories]
        return Response({'categories': data})

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            category = MaterialCategory.objects.create(
                name=request.data.get('name'),
                description=request.data.get('description', '')
            )
            return Response({'message': 'Category created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)