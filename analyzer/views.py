from django.db.models import Avg
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from .github_service import get_github_repos, get_github_profile
from .portfolio_analyzer import analyze_portfolio
from .models import ReportHistory, UserProfile
from .decorators import limit_usage, pro_required

# Optional imports for payment processing
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    razorpay = None

# Optional imports for analytics
try:
    from .analytics import track_portfolio_analysis, track_user_signup, track_user_login
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    track_portfolio_analysis = None
    track_user_signup = None
    track_user_login = None

# Optional imports for AI report
try:
    from .ai_report import generate_ai_report
    AI_REPORT_AVAILABLE = True
except ImportError:
    AI_REPORT_AVAILABLE = False
    generate_ai_report = None

import hashlib
import json

def test_view(request):
    """Simple test view to debug issues"""
    return JsonResponse({
        "status": "working",
        "method": request.method,
        "user_authenticated": request.user.is_authenticated,
        "path": request.path,
        "get_params": dict(request.GET),
        "post_params": dict(request.POST)
    })

def landing(request):
    """Simple landing page view"""
    try:
        return render(request, "index.html")
    except Exception as e:
        # Fallback response if template fails
        return JsonResponse({
            "error": "Template rendering failed",
            "details": str(e),
            "template": "index.html",
            "user_authenticated": request.user.is_authenticated
        })

 

@limit_usage
def analyze(request):
    report = None
    ai_feedback = None
    profile = None
    error_message = None
    
    # Get user profile (decorator ensures it exists)
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            # This shouldn't happen with the decorator, but just in case
            user_profile = UserProfile.objects.create(
                user=request.user,
                is_pro=False,
                free_usage_count=0
            )

    if request.method == "POST":
        username = request.POST.get("username")

        # Check if user can analyze (this is double-checked by decorator)
        if request.user.is_authenticated and user_profile and not user_profile.can_analyze:
            messages.error(request, "You've used your free analysis. Upgrade to Pro to continue!")
            return redirect('upgrade')

        profile = get_github_profile(username)
        if not profile:
            error_message = "GitHub profile not found. Please check username."
        else:
            repos = get_github_repos(username)

            if repos is None:
                error_message = "Unable to fetch repositories from GitHub."
            else:
                report = analyze_portfolio(repos)
                try:
                    ai_feedback = generate_ai_report(report)
                except Exception as e:
                    error_message = str(e)

                if report:
                    if request.user.is_authenticated and user_profile:
                        ReportHistory.objects.create(
                            user=request.user,
                            username=username,
                            score=report['score'],
                            repo_count=report['repo_count'],
                            stars=report['stars'],
                            language_counts=report.get('language_counts', {}),
                            top_languages=report.get('top_languages', []),
                            strengths=report.get('strengths', []),
                            weaknesses=report.get('weaknesses', []),
                            ai_feedback=ai_feedback if ai_feedback else "",
                        )
                        
                        # Increment free usage count for non-pro users
                        if not user_profile.is_pro:
                            user_profile.free_usage_count += 1
                            user_profile.save()
                        
                        # Track portfolio analysis
                        if ANALYTICS_AVAILABLE and track_portfolio_analysis:
                            track_portfolio_analysis(
                                user_id=request.user.id,
                                username=username,
                                score=report.get('score')
                            )
                
    if request.user.is_authenticated:
        archives = ReportHistory.objects.filter(user=request.user).order_by('-created_at')[:12]
    else:
        archives = []

    return render(request, "analyze.html", {
        "report": report,
        "ai_feedback": ai_feedback,
        "profile": profile,
        "error_message": error_message,
        "archives": archives,
        "user_profile": user_profile,
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Track user signup
            if ANALYTICS_AVAILABLE and track_user_signup:
                track_user_signup(user.id)
            return redirect('analyze')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Track user login
            if ANALYTICS_AVAILABLE and track_user_login:
                track_user_login(user.id)
            return redirect('analyze')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def history(request):
    archives = ReportHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'archives': archives})


@require_POST
@csrf_protect
def delete_report(request, report_id):
    if request.user.is_authenticated:
        try:
            report = ReportHistory.objects.get(id=report_id, user=request.user)
            report.delete()
            return JsonResponse({'success': True})
        except ReportHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Report not found'})
    return JsonResponse({'success': False, 'error': 'Not authenticated'})

@login_required
def upgrade(request):
    """Upgrade page for Pro subscription"""
    # Get user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            is_pro=False,
            free_usage_count=0
        )
    
    return render(request, 'upgrade.html', {
        'user_profile': user_profile,
    })


def upgrade_to_pro(request):
    """Handle upgrade to Pro (placeholder for payment)"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            is_pro=False,
            free_usage_count=0
        )
    
    # Upgrade to Pro (in real app, this would be after payment)
    user_profile.is_pro = True
    user_profile.save()
    
    messages.success(request, "🎉 Welcome to Pro! You now have unlimited access to all features.")
    return redirect('analyze')


@login_required
def profile(request):
    # Get user statistics
    user_analyses = ReportHistory.objects.filter(user=request.user)
    total_analyses = user_analyses.count()
    unique_profiles = user_analyses.values('username').distinct().count()
    
    # Get user profile for usage info
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            is_pro=False,
            free_usage_count=0
        )
    
    # Calculate average score
    avg_score = user_analyses.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    average_score = round(avg_score, 1)
    
    # Get recent analyses
    recent_analyses = user_analyses.order_by('-created_at')[:5]
    
    return render(request, 'profile.html', {
        'total_analyses': total_analyses,
        'unique_profiles': unique_profiles,
        'average_score': average_score,
        'recent_analyses': recent_analyses,
        'user_profile': user_profile,
    })


@require_POST
@csrf_protect
def payment_success(request):
    """Handle Razorpay payment success and verify signature"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if not RAZORPAY_AVAILABLE:
        return JsonResponse({'error': 'Payment service not available'}, status=503)
    
    try:
        # Get payment details from request
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'error': 'Missing payment details'}, status=400)
        
        # Initialize Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET)
        )
        
        # Verify signature
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid payment signature'}, status=400)
        
        # Get user profile and upgrade to Pro
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(
                user=request.user,
                is_pro=False,
                free_usage_count=0
            )
        
        # Upgrade user to Pro
        user_profile.is_pro = True
        user_profile.save()
        
        # Store payment details (optional - you can create a Payment model)
        # For now, we'll just show success message
        
        messages.success(request, "🎉 Payment successful! Welcome to Pro!")
        return JsonResponse({'success': True, 'redirect_url': '/analyze/'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_failure(request):
    """Handle payment failure"""
    messages.error(request, "Payment failed. Please try again.")
    return redirect('upgrade')


@login_required
def create_payment_order(request):
    """Create Razorpay payment order"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if not RAZORPAY_AVAILABLE:
        return JsonResponse({'error': 'Payment service not available'}, status=503)
    
    # Get user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            is_pro=False,
            free_usage_count=0
        )
    
    # Check if already pro
    if user_profile.is_pro:
        return JsonResponse({'error': 'Already a Pro user'}, status=400)
    
    # Initialize Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET)
    )
    
    # Create order
    try:
        # Amount in paise (₹199 = 19900 paise)
        amount = 19900
        order_data = {
            'amount': amount,
            'currency': settings.RAZORPAY_CURRENCY,
            'payment_capture': '1',
            'notes': {
                'user_id': request.user.id,
                'username': request.user.username,
                'upgrade_to_pro': 'True'
            }
        }
        
        order = client.order.create(data=order_data)
        
        return JsonResponse({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID,
            'name': 'DevPortfolio Pro',
            'description': 'Upgrade to Pro - Unlimited GitHub Analyses',
            'image': 'https://your-domain.com/static/logo.png',  # Optional
            'prefill': {
                'name': request.user.username,
                'email': f'{request.user.username}@example.com',  # Optional
                'contact': '',  # Optional
            },
            'theme': {
                'color': '#3399cc'
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)