from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Branch
from .serializers import BranchSerializer, BranchCreateSerializer

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
