from rest_framework import serializers
from .models import Chat, User, Message, CommonMessage, Group, GroupUser, GroupMessage

class ChatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    # Explicitly include the reply_to field as a primary key related field.
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Message
        fields = "__all__"

class CommonMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommonMessage
        fields = "__all__"

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(required=True)
    
    class Meta:
        model = Group
        fields = "__all__"

class GroupUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GroupUser
        fields = "__all__"

class GroupMessageSerializer(serializers.HyperlinkedModelSerializer):
    # Include reply_to for group messages as well.
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=GroupMessage.objects.all(), required=False, allow_null=True
    )
    
    class Meta:
        model = GroupMessage
        fields = "__all__"
