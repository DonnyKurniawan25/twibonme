from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'views_count')
    search_fields = ('title', 'description')
    readonly_fields = ('views_count',)
