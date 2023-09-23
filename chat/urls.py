from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_convo, name='start_convo'),
    path('<int:convo_id>/', views.get_conversation, name='get_conversation'),
    path('update/<int:conversation_id>/', views.update_conversation, name='update_conversation'),
    path('', views.conversations, name='conversations')
]