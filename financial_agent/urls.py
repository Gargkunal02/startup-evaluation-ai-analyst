from django.urls import path

from financial_agent.views import chat_bot

urlpatterns = [
    path('chat', chat_bot, name='bbps_user_info'),
]
