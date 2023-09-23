from django.shortcuts import render
from .models import Conversation, YouTubeVideo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import MyUser as User
from .serializers import ConversationListSerializer, ConversationSerializer
from django.db.models import Q
from django.shortcuts import redirect, reverse
from rest_framework import status

# Create your views here.
@api_view(['POST'])
def start_convo(request, ):
    data = request.data
    youtube_video_id = data.pop('youtube_video_id', '')
    video_title = data.pop('youtube_video_title', '')
    video_script = data.pop('youtube_video_script', '')
    video_description = data.pop('youtube_video_description', '')
    video_tags = data.pop('youtube_video_tags', '')
    video_start_time = data.get('video_start_time')
    video_end_time = data.get('video_end_time')
    include_title = data.get('include_title', False)
    include_description = data.get('include_description', False)
    include_tags = data.get('include_tags', False)

    # Check if the YouTube video ID is provided
    if not youtube_video_id:
        return Response({'message': 'You need to provide a YouTube video ID'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        participant = YouTubeVideo.objects.get(video_id=youtube_video_id)
    except YouTubeVideo.DoesNotExist:
        participant = YouTubeVideo.objects.create(video_id=youtube_video_id, 
                                                    title=video_title, 
                                                    script=video_script, 
                                                    description=video_description, 
                                                    tags=video_tags,
                                                    start_time=video_start_time,
                                                    end_time=video_end_time,
                                                    include_title=include_title,
                                                    include_description=include_description,
                                                    include_tags=include_tags)

    conversation = Conversation.objects.filter(Q(initiator=request.user, youtube_video=participant))
    if conversation.exists():
        return redirect(reverse('get_conversation', args=(conversation[0].id,)))
    else:
        conversation = Conversation.objects.create(initiator=request.user, youtube_video=participant)
        return Response(ConversationSerializer(instance=conversation).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_conversation(request, convo_id):
    conversation = Conversation.objects.filter(id=convo_id)
    if not conversation.exists():
        return Response({'message': 'Conversation does not exist'})
    else:
        serializer = ConversationSerializer(instance=conversation[0])
        return Response(serializer.data)


@api_view(['POST'])
def update_conversation(request, conversation_id):
    data = request.data
    video_start_time = data.get('video_start_time', 0.0)
    video_end_time = data.get('video_end_time', 0.0)
    video_script = data.get('video_script', '')
    include_title = data.get('include_title', False)
    include_description = data.get('include_description', False)
    include_tags = data.get('include_tags', False)

    try:
        conversation = Conversation.objects.get(id=conversation_id)
        youtube_video = conversation.youtube_video

        if youtube_video is None:
            return Response({'message': 'YouTube video does not exist for this conversation.'}, status=status.HTTP_404_NOT_FOUND)
        
        youtube_video.start_time = video_start_time
        youtube_video.end_time = video_end_time
        youtube_video.script = video_script
        youtube_video.include_title = include_title
        youtube_video.include_description = include_description
        youtube_video.include_tags = include_tags
        youtube_video.save()

        return Response({'message': 'YouTube video preferences updated successfully.'}, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response({'message': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def conversations(request):
    conversation_list = Conversation.objects.filter(Q(initiator=request.user))
    serializer = ConversationListSerializer(instance=conversation_list, many=True)
    return Response(serializer.data)
