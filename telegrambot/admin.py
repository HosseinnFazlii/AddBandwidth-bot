# telegrambot/admin.py

from django.contrib import admin
from .models import DataCenter

@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'port', 'created_at')
    search_fields = ('name', 'ip_address')
