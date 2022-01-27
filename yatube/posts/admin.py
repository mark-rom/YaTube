from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """PostAdmin class states the structure of administrators space of a web-site.
    """
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
