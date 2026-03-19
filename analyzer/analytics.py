"""
Analytics tracking for DevPortfolio Analyzer
Tracks user interactions, feature usage, and system performance
"""

import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from .models import ReportHistory

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Simple analytics tracking system"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        
    def track_event(self, event_name, properties=None, user_id=None):
        """
        Track an analytics event
        
        Args:
            event_name: Name of the event (e.g., 'portfolio_analyzed', 'pdf_downloaded')
            properties: Dictionary of event properties
            user_id: User ID if authenticated
        """
        try:
            # Get current analytics data from cache
            analytics_data = cache.get('analytics_data', {})
            
            # Initialize date key
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in analytics_data:
                analytics_data[today] = {'events': {}, 'users': set()}
            
            # Track event
            if event_name not in analytics_data[today]['events']:
                analytics_data[today]['events'][event_name] = 0
            analytics_data[today]['events'][event_name] += 1
            
            # Track unique users
            if user_id:
                analytics_data[today]['users'].add(user_id)
            
            # Store back in cache
            cache.set('analytics_data', analytics_data, self.cache_timeout * 24)  # 24 hours
            
            logger.info(f"Analytics event tracked: {event_name}")
            
        except Exception as e:
            logger.error(f"Error tracking analytics event: {e}")
    
    def get_daily_stats(self, days=7):
        """Get analytics statistics for the last N days"""
        try:
            analytics_data = cache.get('analytics_data', {})
            stats = {}
            
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                if date in analytics_data:
                    stats[date] = {
                        'events': analytics_data[date]['events'],
                        'unique_users': len(analytics_data[date]['users'])
                    }
                else:
                    stats[date] = {'events': {}, 'unique_users': 0}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        try:
            # Database metrics
            total_reports = ReportHistory.objects.count()
            unique_users = ReportHistory.objects.values('user').distinct().count()
            avg_score = ReportHistory.objects.aggregate(avg_score=Avg('score'))['avg_score'] or 0
            
            # Recent activity
            last_24h = datetime.now() - timedelta(hours=24)
            recent_reports = ReportHistory.objects.filter(created_at__gte=last_24h).count()
            
            # Top languages
            top_languages = self._get_top_languages()
            
            return {
                'total_reports': total_reports,
                'unique_users': unique_users,
                'average_score': round(avg_score, 1),
                'reports_last_24h': recent_reports,
                'top_languages': top_languages,
                'cache_hit_rate': self._get_cache_hit_rate(),
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _get_top_languages(self, limit=5):
        """Get top programming languages from reports"""
        try:
            # This is a simplified version - in production you'd want proper aggregation
            languages = {}
            reports = ReportHistory.objects.all()[:100]  # Sample for performance
            
            for report in reports:
                if report.language_counts:
                    for lang, count in report.language_counts.items():
                        if lang not in languages:
                            languages[lang] = 0
                        languages[lang] += count
            
            # Sort and return top N
            sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            return [{'language': lang, 'count': count} for lang, count in sorted_languages[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting top languages: {e}")
            return []
    
    def _get_cache_hit_rate(self):
        """Get cache hit rate (simplified)"""
        try:
            # This is a placeholder - in production you'd use Redis metrics
            return 0.85  # Example value
        except:
            return 0

# Global analytics tracker instance
analytics = AnalyticsTracker()

def track_portfolio_analysis(user_id=None, username=None, score=None):
    """Track portfolio analysis event"""
    properties = {
        'username': username,
        'score_range': _get_score_range(score) if score else 'unknown'
    }
    analytics.track_event('portfolio_analyzed', properties, user_id)

def track_pdf_download(user_id=None):
    """Track PDF download event"""
    analytics.track_event('pdf_downloaded', None, user_id)

def track_user_signup(user_id):
    """Track user signup event"""
    analytics.track_event('user_signup', None, user_id)

def track_user_login(user_id):
    """Track user login event"""
    analytics.track_event('user_login', None, user_id)

def track_report_deleted(user_id):
    """Track report deletion event"""
    analytics.track_event('report_deleted', None, user_id)

def _get_score_range(score):
    """Get score range category"""
    if score >= 70:
        return 'high'
    elif score >= 40:
        return 'medium'
    else:
        return 'low'
