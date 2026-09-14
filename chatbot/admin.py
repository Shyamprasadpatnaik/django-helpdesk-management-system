from django.contrib import admin
from .models import ChatbotConversation, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')

@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'session_id', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'user__employee_id')
    inlines = [ChatMessageInline]
