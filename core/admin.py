from django.contrib import admin

# Register your models here.
from .models import Profile, Connection

admin.site.register(Profile)
admin.site.register(Connection)