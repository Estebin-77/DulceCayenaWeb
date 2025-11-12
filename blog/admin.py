from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    list_display = ('titulo', 'autor', 'created')
    search_fields = ('titulo', 'contenido')
    list_filter = ('autor', 'created')

