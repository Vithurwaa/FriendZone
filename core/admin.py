from django.contrib import admin
from .models import (
    Profile,
    Connection,
    Activity,
    ActivityJoin,
    Interest,
    Report,
    Post
)

# ================= PROFILE ADMIN =================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "city", "gender")
    search_fields = ("user__username", "city")
    list_filter = ("gender", "city")


# ================= CONNECTION ADMIN =================

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status")
    list_filter = ("status",)
    search_fields = ("sender__username", "receiver__username")


# ================= ACTIVITY ADMIN =================

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "location", "date", "status")
    list_filter = ("status", "date")
    search_fields = ("title", "creator__username")


# ================= ACTIVITY JOIN ADMIN =================

@admin.register(ActivityJoin)
class ActivityJoinAdmin(admin.ModelAdmin):
    list_display = ("user", "activity")
    search_fields = ("user__username", "activity__title")


# ================= INTEREST ADMIN =================

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("name",)


# ================= REPORT ADMIN =================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported_user", "created_at")
    search_fields = ("reporter__username", "reported_user__username")
    readonly_fields = ("created_at",)


# ================= POST ADMIN =================

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)