from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Branch
from .serializers import BranchSerializer, BranchCreateSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_branches_simple(request):
    branches = Branch.objects.all().order_by('name')
    data = []
    for branch in branches:
        data.append({
            'id': branch.id,
            'name': branch.name,
            'location': branch.location
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_branches(request):
    branches = Branch.objects.all()
    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_branch(request):
    serializer = BranchCreateSerializer(data=request.data)
    if serializer.is_valid():
        branch = serializer.save()
        return Response(BranchSerializer(branch).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def assign_branch_admin(request, branch_id):
    """Assign an admin to a branch"""
    try:
        branch = Branch.objects.get(pk=branch_id)
        admin_id = request.data.get('admin')

        if admin_id:
            from users.models import CustomUser
            try:
                admin = CustomUser.objects.get(pk=admin_id, branch=branch)
                branch.admin = admin
                branch.save()
                return Response(BranchSerializer(branch).data)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found in this branch'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            branch.admin = None
            branch.save()
            return Response(BranchSerializer(branch).data)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
