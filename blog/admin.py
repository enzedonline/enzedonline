from django.contrib import admin
from django_comments_xtd.admin import XtdCommentsAdmin
from .models import CustomComment

class CustomCommentAdmin(XtdCommentsAdmin):
    list_display = ('cid', 'name', 'page', 'object_pk',
                    'ip_address', 'submit_date', 'followup', 'is_public',
                    'is_removed')
    fieldsets = (
        (None, {'fields': ('content_type', 'page', 'object_pk', 'site')}),
        ('Content', {'fields': ('user', 'user_name', 'user_email',
                                'user_url', 'comment', 'followup')}),
        ('Metadata', {'fields': ('submit_date', 'ip_address',
                                 'is_public', 'is_removed')}),
    )

admin.site.register(CustomComment, CustomCommentAdmin)

