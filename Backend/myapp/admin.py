from django.contrib import admin
from .models import User, Bot, Moderator
# Register your models here.

admin.site.register(User)
admin.site.register(Bot)
admin.site.register(Moderator)