from django.shortcuts import render
from rest_framework import viewsets
from .serializers import (
    UserSerializer,
    ChatSerializer,
    MessageSerializer,
    CommonMessageSerializer,
    GroupUserSerializer,
    GroupSerializer,
    GroupMessageSerializer
)
from .models import User, Chat, Message, CommonMessage, GroupUser, Group, GroupMessage
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

class CommonMessageViewSet(viewsets.ModelViewSet):
    queryset = CommonMessage.objects.all()
    serializer_class = CommonMessageSerializer
         
class GroupUserViewSet(viewsets.ModelViewSet):
    queryset = GroupUser.objects.all()
    serializer_class = GroupUserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GroupMessageViewSet(viewsets.ModelViewSet):
    queryset = GroupMessage.objects.all()
    serializer_class = GroupMessageSerializer
    # Added parser_classes so that group messages can handle JSON and multipart/form-data (for files)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
