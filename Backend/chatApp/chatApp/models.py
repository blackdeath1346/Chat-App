from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class User(models.Model):
    """
    Represents a user with a unique username.
    """
    id = models.CharField(max_length=50, primary_key=True, unique=True)  # Same as username
    username = models.CharField(max_length=50, unique=True)  # Keeping username field
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Ensure id is always the same as username
        if not self.id:
            self.id = self.username
        super().save(*args, **kwargs)


class Chat(models.Model):
    """
    Represents a unique chat between two users.
    """
    id = models.CharField(max_length=101, primary_key=True, unique=True, editable=False)  # Stores "username1-username2"
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")  # Ensures unique chat per user pair

    def save(self, *args, **kwargs):
        # Generate unique id based on usernames (sorted to maintain consistency)
        self.id = f"{min(self.user1.username, self.user2.username)}-{max(self.user1.username, self.user2.username)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"


class Message(models.Model):
    """
    Represents a message in a chat.
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_files/', null=True, blank=True)
    # New reply_to field (nullable self-reference)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat}"


class Group(models.Model):
    """
    Represents a group with an admin and a unique name.
    """
    id = models.CharField(max_length=50, primary_key=True)  # User-defined ID
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_groups")
    
    def __str__(self):
        return self.name


class GroupUser(models.Model):
    """
    Represents a user who is a member of a group.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="groups")
    
    class Meta:
        unique_together = ("group", "user")  # Ensures a user can't be added twice to the same group
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class GroupMessage(models.Model):
    """
    Represents a message sent in a group.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages")
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_files/', null=True, blank=True)
    # New reply_to field (nullable self-reference)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_replies')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}"


class CommonMessage(models.Model):
    """
    Stores broadcast messages for all users.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="broadcasted_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast from {self.sender.username}"


@receiver(post_save, sender=User)
def create_chats_for_new_user(sender, instance, created, **kwargs):
    """
    Signal to create chats when a new user is added.
    """
    if created:
        existing_users = User.objects.exclude(id=instance.id)  # Exclude the newly created user
        for user in existing_users:
            user1, user2 = sorted([instance, user], key=lambda x: x.username)
            chat_id = f"{user1.username}-{user2.username}"
            Chat.objects.get_or_create(id=chat_id, user1=user1, user2=user2)


@receiver(post_save, sender=Message)
def notify_users_on_new_message(sender, instance, created, **kwargs):
    """
    Signal to notify the WebSocket consumer when a new message is created.
    """
    if created:  # Only notify when a new message is sent
        channel_layer = get_channel_layer()
        chat_group_name = f"chat_{instance.chat.id}"
        async_to_sync(channel_layer.group_send)(
            chat_group_name,
            {
                "type": "chat.message",
                "message": {
                    "sender": instance.sender.username,
                    "content": instance.content,
                    "timestamp": instance.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "file_attachment": instance.file_attachment.url if instance.file_attachment else None,
                    "reply_to": instance.reply_to.id if instance.reply_to else None,
                }
            }
        )


@receiver(post_save, sender=GroupMessage)
def notify_users_on_new_group_message(sender, instance, created, **kwargs):
    """
    Signal to notify the WebSocket consumer when a new group message is created.
    """
    if created:
        channel_layer = get_channel_layer()
        group_group_name = f"group_{instance.group.id}"
        async_to_sync(channel_layer.group_send)(
            group_group_name,
            {
                "type": "group.message",
                "message": {
                    "sender": instance.sender.username,
                    "content": instance.content,
                    "timestamp": instance.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "file_attachment": instance.file_attachment.url if instance.file_attachment else None,
                    "reply_to": instance.reply_to.id if instance.reply_to else None,
                }
            }
        )


@receiver(post_save, sender=CommonMessage)
def notify_users_on_new_broadcast(sender, instance, created, **kwargs):
    """
    Signal to notify the WebSocket consumer when a new broadcast message is created.
    """
    if created:  # Only notify when a new message is sent
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",  # Send to the global WebSocket group
            {
                "type": "broadcast.message",
                "message": {
                    "sender": instance.sender.username,  # Ensure it's the username, not the ID
                    "content": instance.content,
                    "timestamp": instance.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
        )
