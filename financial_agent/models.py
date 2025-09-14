from django.db import models

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)  # Add user_id to associate history with users
    role = models.CharField(max_length=50)  # 'user' or 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} - Session {self.session_id} - {self.role}: {self.content[:50]}"