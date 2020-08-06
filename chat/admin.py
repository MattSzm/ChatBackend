from django.contrib import admin
from chat.models import Chat, ChatParticipantConnector


class UserInline(admin.StackedInline):
    model = ChatParticipantConnector
    raw_id_fields = ['participant']


class ChatAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'name','created','last_activity_date']
    ordering = ('-last_activity_date',)
    inlines = [UserInline]

admin.site.register(Chat, ChatAdmin)