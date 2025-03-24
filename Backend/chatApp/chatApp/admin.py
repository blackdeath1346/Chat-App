from django.contrib import admin
from .models import User
from .models import Chat
from .models import Message
from .models import CommonMessage
from .models import GroupUser
from .models import Group
from .models import GroupMessage
#from .models import CommonMessage

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(CommonMessage)
admin.site.register(GroupUser)
admin.site.register(Group)
admin.site.register(GroupMessage)
#admin.site.register(CommonMessage)