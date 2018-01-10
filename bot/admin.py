from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, User

admin.site.register(BotUser)
admin.site.register(Settings)
admin.site.register(Log)
admin.site.register(Txs)
admin.site.register(Compaign)


admin.site.unregister(Group)
admin.site.unregister(User)
