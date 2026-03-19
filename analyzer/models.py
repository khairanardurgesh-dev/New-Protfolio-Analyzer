from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    is_pro = models.BooleanField(default=False)
    free_usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username} - {'Pro' if self.is_pro else 'Free'} ({self.free_usage_count}/1 used)"
    
    @property
    def has_free_usage_left(self):
        """Check if user has free usage left"""
        return not self.is_pro and self.free_usage_count < 1
    
    @property
    def can_analyze(self):
        """Check if user can perform analysis"""
        return self.is_pro or self.free_usage_count < 1


class ReportHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_history")
    username = models.CharField(max_length=39)
    score = models.IntegerField()
    repo_count = models.IntegerField()
    stars = models.IntegerField()
    language_counts = models.JSONField(default=dict)
    top_languages = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    ai_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.username} ({self.score})"
