from django.urls import path
from . import views

urlpatterns = [
    # AI Chat Page
    path('ai-assistant/', views.chat_page_view, name='ai_assistant'),
    
    # AI APIs
    path('api/ai/chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/ai/parse-voice/', views.parse_voice_api, name='parse_voice_api'),
    path('api/ai/insights/', views.ai_insights_api, name='ai_insights_api'),
]
