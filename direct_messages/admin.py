from django.contrib import admin
from .models import ChattingRoom, Message
# Register your models here.

@admin.register(ChattingRoom)
class Admin(admin.ModelAdmin):
    list_display=(
        "__str__",
        "created_at",
        "updated_at",
    )
    list_filter=(
        "updated_at",
    )


@admin.register(Message)
class Admin(admin.ModelAdmin):
    list_display=(
        "text",
        "user",
        "room",
        "created_at"
    )
    list_filter=(
        "created_at",
    )