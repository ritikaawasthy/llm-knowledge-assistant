from django.contrib import admin

# Register your models here.

# knowledge/admin.py
from django.contrib import admin
from .models import Document, Chunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "page_number", "chunk_id")
    search_fields = ("text",)
