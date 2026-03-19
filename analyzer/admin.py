from django.contrib import admin
from .models import ReportHistory


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'score', 'repo_count', 'stars', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'username')
