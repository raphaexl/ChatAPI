from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.
# def create_hash():
#     return str(uuid.uuid4())

class YouTubeVideo(models.Model):
    video_id = models.CharField(_("Video ID"),max_length=20)  # Adjust the max length as needed
    # hash = models.CharField(max_length=128, default=create_hash, unique=True)
    title = models.CharField(_("Title"), max_length=256, null=True)
    script = models.TextField(_("Script"),  blank=True, null=True)
    description =  models.TextField(_("Description"), blank=True, null=True)
    tags =  models.CharField(_("Tags"), max_length=512, blank=True, null=True)
    
    start_time = models.FloatField(default=0.0)
    end_time = models.FloatField(default=0.0)
    include_title = models.BooleanField(default=False)
    include_description = models.BooleanField(default=False)
    include_tags = models.BooleanField(default=False)

    def __str__(self):
        return self.video_id

class Conversation(models.Model):
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="convo_starter"
    )

    youtube_video = models.ForeignKey(YouTubeVideo, on_delete=models.CASCADE, null=True, default=None)
    start_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    class MessageType(models.TextChoices):
        System = 'SY', ('System')
        User = 'US', ('User')
        Assistant = 'AS', ('Assistant')

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                               related_name='message_sender')
    text = models.CharField(max_length=500)
    attachment = models.FileField(blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True)
    message_type = models.CharField(max_length=2,choices=MessageType.choices,default=MessageType.User,)

    class Meta:
        ordering = ('timestamp',)
    
    def __str__(self):
        return f"Message from {'User' if self.is_from_user else 'YouTube Video'} in conversation {self.conversation_id}"
