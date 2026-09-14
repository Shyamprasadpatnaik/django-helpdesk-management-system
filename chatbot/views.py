import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .models import ChatbotConversation, ChatMessage
from services.ai_service import generate_ai_response

@login_required
def chatbot_page(request):
    """
    Dedicated AI triage and troubleshooting workspace for employees.
    """
    # Fetch or create recent session
    conversation = ChatbotConversation.objects.filter(user=request.user).first()
    if not conversation:
        conversation = ChatbotConversation.objects.create(user=request.user)

    messages_list = conversation.messages.all()

    return render(request, 'chatbot/assistant.html', {
        'conversation': conversation,
        'messages_list': messages_list,
    })


@login_required
@csrf_protect
def chatbot_api(request):
    """
    AJAX endpoint receiving message and returning AI triage response.
    Gracefully falls back to offline guidance if network or API key fails.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not user_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Retrieve conversation
        if session_id:
            conversation, _ = ChatbotConversation.objects.get_or_create(session_id=session_id, user=request.user)
        else:
            conversation = ChatbotConversation.objects.create(user=request.user)

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_text
        )

        # Prepare short context history
        history = list(conversation.messages.order_by('-created_at')[:6].values('role', 'content'))
        history.reverse()

        # Call AI service
        ai_result = generate_ai_response(user_text, conversation_history=history)

        reply_text = ai_result.get('reply', 'I could not process your request at this moment.')
        suggested_dept = ai_result.get('suggested_dept')
        suggested_cat = ai_result.get('suggested_category')
        provider = ai_result.get('provider', 'Assistant')

        # Save assistant message
        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=reply_text
        )

        return JsonResponse({
            'status': 'success',
            'session_id': str(conversation.session_id),
            'reply': reply_text,
            'suggested_dept': suggested_dept,
            'suggested_category': suggested_cat,
            'provider': provider
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'reply': "AI assistant is temporarily unavailable. You can still create a support ticket directly.",
            'error': str(e)
        }, status=200)
