from django.contrib import admin

from notifications.models import Notification, LinkButton


class LinkButtonInline(admin.StackedInline):
    model = LinkButton
    extra = 0
    fields = ('text_rus', 'text_heb', 'link',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.started:
            return [field.name for field in self.model._meta.fields]
        else:
            return []


@admin.register(Notification)
class Notification(admin.ModelAdmin):
    list_display = ('notify_time', 'target', 'is_valid', 'started', 'notified', 'curr_status',)
    list_filter = ('is_valid', 'started', 'notified', 'target',)
    fields = ('target', 'user', 'text_rus', 'text_heb', 'notify_time', 'image',)
    inlines = (LinkButtonInline,)
    autocomplete_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.started:
            return [field.name for field in self.model._meta.fields]
        else:
            return []
    
    def curr_status(self, obj):
        if obj and obj.total_users > 0:
            return f'{obj.success_users}/{obj.total_send_users}/{obj.total_users}'
        
        return '-/-/-'
    
    curr_status.short_description = 'Успешно/Отправлено/Всего'