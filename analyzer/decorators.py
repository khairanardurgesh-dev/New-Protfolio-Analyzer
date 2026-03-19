from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import UserProfile


def limit_usage(view_func):
    """
    Decorator to limit usage based on freemium model
    Blocks access if user has exceeded free usage limit and is not pro
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Allow access if user is not authenticated (they'll be redirected to login)
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get or create user profile
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(
                user=request.user,
                is_pro=False,
                free_usage_count=0
            )
        
        # Check if user can analyze
        if not profile.can_analyze:
            messages.error(
                request, 
                "You've used your free analysis. Upgrade to Pro to continue using the tool!"
            )
            return redirect('upgrade')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def pro_required(view_func):
    """
    Decorator to require pro status
    Blocks access if user is not pro
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Allow access if user is not authenticated (they'll be redirected to login)
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get or create user profile
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(
                user=request.user,
                is_pro=False,
                free_usage_count=0
            )
        
        # Check if user is pro
        if not profile.is_pro:
            messages.error(
                request, 
                "This feature requires a Pro subscription. Upgrade to unlock!"
            )
            return redirect('upgrade')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
