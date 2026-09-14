import uuid
from django.db import models
from django.conf import settings

class ChatbotConversation(models.Model):
    """
    Session tracking an employee's troubleshooting conversation with the AI assistant.
    """
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chatbot_conversations'
    )
    title = models.CharField(max_length=150, default="Issue Troubleshooting Session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.title} ({self.created_at.strftime('%d %b %H:%M')})"


class ChatMessage(models.Model):
    """
    Single message turn in a chatbot troubleshooting dialogue.
    """
    conversation = models.ForeignKey(
        ChatbotConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=20,
        choices=[('user', 'User'), ('assistant', 'AI Assistant')],
        default='user'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}"
