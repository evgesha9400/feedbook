from django.contrib import admin
from .models import *

admin.site.register(Session)
admin.site.register(Message)
admin.site.register(Answer)
admin.site.register(SessionQuestion)
