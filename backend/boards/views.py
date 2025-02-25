from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.contrib.auth import get_user_model
from .models import Board, BoardMembership
from .serializers import BoardSerializer, BoardDetailSerializer, BoardMembershipSerializer
from .permissions import IsBoardAdminOrReadOnly, IsBoardMember

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
   
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsBoardAdminOrReadOnly]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsBoardMember]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Board.objects.filter(is_public=True)
            
        return Board.objects.filter(
            models.Q(members=user) | models.Q(is_public=True)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsBoardAdminOrReadOnly])
    def add_member(self, request, pk=None):
        board = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', BoardMembership.Role.CONTRIBUTOR)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if board.members.filter(id=user.id).exists():
            return Response(
                {'error': 'User is already a member of this board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = BoardMembership.objects.create(
            user=user,
            board=board,
            role=role
        )
        
        serializer = BoardMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsBoardAdminOrReadOnly])
    def remove_member(self, request, pk=None):
        board = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            membership = BoardMembership.objects.get(user=user, board=board)
        except BoardMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.id == board.created_by.id:
            return Response(
                {'error': 'Cannot remove the board creator'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        board = self.get_object()
        user = request.user
        
        if not board.is_public:
            return Response(
                {'error': 'Cannot join a private board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if board.members.filter(id=user.id).exists():
            return Response(
                {'error': 'User is already a member of this board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = BoardMembership.objects.create(
            user=user,
            board=board,
            role=BoardMembership.Role.CONTRIBUTOR
        )
        
        serializer = BoardMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        board = self.get_object()
        user = request.user
        
        try:
            membership = BoardMembership.objects.get(user=user, board=board)
        except BoardMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.id == board.created_by.id:
            return Response(
                {'error': 'Board creator cannot leave. Transfer ownership first or delete the board.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsBoardAdminOrReadOnly])
    def update_member_role(self, request, pk=None):
        board = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not role or role not in [choice[0] for choice in BoardMembership.Role.choices]:
            return Response(
                {'error': f'Invalid role. Choose from {[choice[0] for choice in BoardMembership.Role.choices]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            membership = BoardMembership.objects.get(user=user, board=board)
        except BoardMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this board'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.role = role
        membership.save()
        
        serializer = BoardMembershipSerializer(membership)
        return Response(serializer.data)