from django.contrib import admin
from .models import YouTubeVideo,Conversation, Message

# Register your models here.
admin.site.register(YouTubeVideo)
admin.site.register(Conversation)
admin.site.register(Message)