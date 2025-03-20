"""Настройка админ-зоны."""
from django.contrib import admin

from .models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    """Класс, улучшающий работу с таблицей Post."""

    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = (
        'title',
        'is_published',
        'category',
    )
    list_filter = ('pub_date',)
    list_display_links = ('title', 'pub_date',)


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
