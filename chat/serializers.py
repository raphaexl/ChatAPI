from users.serializers import UserSerializer
from .models import YouTubeVideo, Conversation, Message
from rest_framework import serializers


class YouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeVideo
        # fields = '__all__'
        fields = ['video_id', 'title', 'script', 'description', 'tags']
    

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    initiator = UserSerializer()
    youtube_video = YouTubeVideoSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['initiator', 'youtube_video', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.first()
        if message:
            return MessageSerializer(instance=message).data
        else:
            return None


class ConversationSerializer(serializers.ModelSerializer):
    initiator = UserSerializer()
    youtube_video = YouTubeVideoSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['initiator', 'youtube_video', 'message_set']
