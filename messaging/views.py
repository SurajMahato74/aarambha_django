from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Group, Message, MessageRequest
from notices.models import UserNotification
import json

User = get_user_model()

def member_list(request):
    """Member list with filtering"""
    users = User.objects.exclude(id=request.user.id).select_related('branch').order_by('first_name', 'email')
    
    context = {
        'users': users,
        'branches': User.objects.values_list('branch__name', flat=True).distinct().filter(branch__isnull=False),
        'user_types': ['member', 'volunteer']
    }
    return render(request, 'messaging/member_list.html', context)

def conversations(request):
    """List all conversations and groups"""
    user_conversations = Conversation.objects.filter(participants=request.user)
    user_groups = Group.objects.filter(members=request.user)
    message_requests = MessageRequest.objects.filter(to_user=request.user, status='pending')
    
    # Add other_user to each conversation
    conversations_with_users = []
    for conversation in user_conversations:
        other_user = conversation.participants.exclude(id=request.user.id).first()
        conversations_with_users.append({
            'conversation': conversation,
            'other_user': other_user
        })
    
    context = {
        'conversations': conversations_with_users,
        'groups': user_groups,
        'message_requests': message_requests
    }
    return render(request, 'messaging/conversations.html', context)

def chat(request, type, id):
    """Chat interface for conversation or group"""
    if type == 'user':
        other_user = get_object_or_404(User, id=id)
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=other_user).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)
        
        messages_list = conversation.messages.all().order_by('created_at')
        context = {
            'conversation': conversation,
            'messages': messages_list,
            'other_user': other_user,
            'is_group': False,
        }
    elif type == 'group':
        group = get_object_or_404(Group, id=id, members=request.user)
        messages_list = group.messages.all().order_by('created_at')
        context = {
            'conversation': group,
            'messages': messages_list,
            'other_user': None,
            'is_group': True,
        }
    else:  # conversation
        conversation = get_object_or_404(Conversation, id=id, participants=request.user)
        messages_list = conversation.messages.all().order_by('created_at')
        other_user = conversation.participants.exclude(id=request.user.id).first()
        context = {
            'conversation': conversation,
            'messages': messages_list,
            'other_user': other_user,
            'is_group': False,
        }
    
    return render(request, 'messaging/chat.html', context)

@csrf_exempt
def send_message(request):
    """Send message to conversation or group"""
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')
        type = data.get('type')
        id = data.get('id')
        
        if type == 'conversation':
            conversation = get_object_or_404(Conversation, id=id, participants=request.user)
            message = Message.objects.create(
                sender=request.user,
                conversation=conversation,
                content=content
            )
            conversation.updated_at = message.created_at
            conversation.save()
        else:  # group
            group = get_object_or_404(Group, id=id, members=request.user)
            message = Message.objects.create(
                sender=request.user,
                group=group,
                content=content
            )
            group.updated_at = message.created_at
            group.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def start_conversation(request):
    """Start new conversation or send message request"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message_content = request.POST.get('message')
        
        other_user = get_object_or_404(User, id=user_id)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=other_user).first()
        
        if existing_conversation:
            # Send message directly
            Message.objects.create(
                sender=request.user,
                conversation=existing_conversation,
                content=message_content
            )
            existing_conversation.save()  # Update timestamp
            return redirect('chat', type='conversation', id=existing_conversation.id)
        else:
            # Check if message request already exists
            existing_request = MessageRequest.objects.filter(
                from_user=request.user,
                to_user=other_user
            ).first()
            
            if not existing_request:
                # Create message request
                MessageRequest.objects.create(
                    from_user=request.user,
                    to_user=other_user,
                    message=message_content
                )
                
                # Create notification
                UserNotification.objects.create(
                    user=other_user,
                    notification_type='message_request',
                    title='New Message Request',
                    message=f'{request.user.get_full_name() or request.user.email} wants to message you'
                )
                
                messages.success(request, 'Message request sent!')
            else:
                messages.info(request, 'Message request already sent!')
        
        return redirect('member_list')
    
    return redirect('member_list')

@csrf_exempt
def handle_message_request(request):
    """Accept or reject message request"""
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        message_request = get_object_or_404(MessageRequest, id=request_id, to_user=request.user)
        
        if action == 'accept':
            # Create conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, message_request.from_user)
            
            # Send the original message
            Message.objects.create(
                sender=message_request.from_user,
                conversation=conversation,
                content=message_request.message
            )
            
            message_request.status = 'accepted'
            message_request.save()
            
            messages.success(request, 'Message request accepted!')
            return redirect('chat', type='conversation', id=conversation.id)
        else:
            message_request.status = 'rejected'
            message_request.save()
            messages.info(request, 'Message request rejected!')
        
        return redirect('conversations')
    
    return redirect('conversations')

def create_group(request):
    """Create new group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        member_ids = request.POST.getlist('members')
        
        group = Group.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        
        # Add creator and selected members
        group.members.add(request.user)
        for member_id in member_ids:
            group.members.add(member_id)
        
        messages.success(request, f'Group "{name}" created successfully!')
        return redirect('chat', type='group', id=group.id)
    
    # Get users for group creation
    users = User.objects.exclude(id=request.user.id).select_related('branch')
    context = {
        'users': users,
        'branches': User.objects.values_list('branch__name', flat=True).distinct().filter(branch__isnull=False),
        'user_types': ['member', 'volunteer']
    }
    return render(request, 'messaging/create_group.html', context)

@csrf_exempt
def get_conversation(request, user_id):
    """Get conversation with specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if conversation exists
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other_user).first()
    
    if conversation:
        return JsonResponse({
            'conversation_id': conversation.id,
            'exists': True
        })
    else:
        return JsonResponse({
            'conversation_id': None,
            'exists': False
        })

@csrf_exempt
def get_messages(request, conversation_id):
    """Get messages for conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all().order_by('created_at')
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.email,
            'created_at': message.created_at.isoformat()
        })
    
    return JsonResponse({
        'messages': messages_data
    })

@csrf_exempt
def send_message_ajax(request):
    """Send message via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            group_id = data.get('group_id')
            message_content = data.get('message') or data.get('content')
            
            if not message_content or not message_content.strip():
                return JsonResponse({'error': 'Message content is required'}, status=400)
            
            if group_id:
                # Send to group
                group = get_object_or_404(Group, id=group_id, members=request.user)
                Message.objects.create(
                    sender=request.user,
                    group=group,
                    content=message_content.strip()
                )
                return JsonResponse({'success': True, 'group_id': group.id})
            elif user_id:
                # Send to user
                other_user = get_object_or_404(User, id=user_id)
                conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(participants=other_user).first()
                
                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, other_user)
                
                Message.objects.create(
                    sender=request.user,
                    conversation=conversation,
                    content=message_content.strip()
                )
                return JsonResponse({'success': True, 'conversation_id': conversation.id})
            else:
                return JsonResponse({'error': 'Either user_id or group_id is required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def leave_group(request):
    """Leave group"""
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id, members=request.user)
        
        group.members.remove(request.user)
        messages.success(request, f'Left group "{group.name}"')
        
        return redirect('conversations')
    
    return redirect('conversations')

@csrf_exempt
def user_profile(request, user_id):
    """Get user profile data"""
    user = get_object_or_404(User, id=user_id)
    application = user.applications.first()
    
    data = {
        'success': True,
        'user': {
            'id': user.id,
            'name': user.get_full_name() or user.email,
            'email': user.email,
            'user_type': user.get_user_type_display(),
            'branch': user.branch.name if user.branch else None,
            'phone': user.phone,
            'address': user.address,
            'photo': application.photo.url if application and application.photo else None,
        }
    }
    return JsonResponse(data)