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

# Optional imports for decorators
try:
    from .decorators import limit_usage, pro_required
    DECORATORS_AVAILABLE = True
except ImportError:
    DECORATORS_AVAILABLE = False
    limit_usage = None
    pro_required = None

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

 

def analyze(request):
    """Analyze GitHub portfolio with freemium model"""
    report = None
    ai_feedback = None
    profile = None
    error_message = None
    
    # Initialize session variables for 3 free analyses
    if 'free_analysis_count' not in request.session:
        request.session['free_analysis_count'] = 0
    if 'is_paid' not in request.session:
        request.session['is_paid'] = False
    
    # Check if user can analyze (3 free or paid)
    can_analyze = request.session['free_analysis_count'] < 3 or request.session['is_paid']
    
    if request.method == "POST":
        if not can_analyze:
            # Redirect to payment page if free used and not paid
            return redirect('upgrade')
        
        username = request.POST.get("username")
        
        try:
            # Show loading state
            request.session['analysis_loading'] = True
            
            profile = get_github_profile(username)
            if not profile:
                error_message = "GitHub profile not found. Please check username."
            else:
                repos = get_github_repos(username)
                
                if repos is None:
                    error_message = "Unable to fetch repositories from GitHub."
                else:
                    report = analyze_portfolio(repos)
                    
                    # Generate AI feedback with enhanced error handling
                    try:
                        if AI_REPORT_AVAILABLE and generate_ai_report:
                            ai_feedback = generate_ai_report(report)
                            print(f"✅ AI analysis generated for {username}")
                        else:
                            ai_feedback = "AI analysis temporarily unavailable. Please try again later."
                    except Exception as e:
                        print(f"❌ AI analysis failed: {e}")
                        ai_feedback = f"AI analysis encountered an error: {str(e)}"
            
            # Increment free analysis count
            if not request.session['is_paid']:
                request.session['free_analysis_count'] += 1
                request.session[f'analysis_{request.session["free_analysis_count"]}_username'] = username
                print(f"🔓 Free analysis {request.session['free_analysis_count']}/3 used for {username}")
            
            request.session['analysis_loading'] = False
            request.session.modified = True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            error_message = f"Analysis failed: {str(e)}"
            request.session['analysis_loading'] = False
            request.session.modified = True
    
    return render(request, "analyze.html", {
        "report": report,
        "ai_feedback": ai_feedback,
        "profile": profile,
        "error_message": error_message,
        "archives": [],  # Simplified for debugging
        "user_profile": None,  # Simplified for debugging
        "can_analyze": can_analyze,
        "free_analysis_count": request.session['free_analysis_count'],
        "free_analyses_remaining": max(0, 3 - request.session['free_analysis_count']),
        "is_paid": request.session['is_paid'],
        "analysis_loading": request.session.get('analysis_loading', False),
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
    # Support both authenticated and session-based users
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
        
        # Mark user as paid in session
        request.session['is_paid'] = True
        request.session['payment_completed'] = True
        request.session.modified = True
        
        print(f"✅ Payment successful - user marked as paid")
        
        # If user is authenticated, also update their profile
        if request.user.is_authenticated:
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
            print(f"✅ Authenticated user {request.user.username} upgraded to Pro")
        
        messages.success(request, "🎉 Payment successful! You now have unlimited access to detailed reports!")
        return JsonResponse({'success': True, 'redirect_url': '/analyze/'})
        
    except Exception as e:
        print(f"❌ Payment processing failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def payment_failure(request):
    """Handle payment failure"""
    messages.error(request, "Payment failed. Please try again.")
    return redirect('upgrade')


@require_POST
@csrf_protect
def create_payment_order(request):
    """Create Razorpay payment order"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not RAZORPAY_AVAILABLE:
        return JsonResponse({'error': 'Payment service not available'}, status=503)
    
    # Support both authenticated and session-based users
    user_id = request.user.id if request.user.is_authenticated else request.session.session_key
    username = request.user.username if request.user.is_authenticated else f"session_{request.session.session_key[:8]}"
    
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
                'user_id': str(user_id),
                'username': username,
                'upgrade_to_pro': 'True',
                'session_based': str(not request.user.is_authenticated)
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
                'name': username,
                'email': f'{username}@example.com',  # Optional
                'contact': '',  # Optional
            },
            'theme': {
                'color': '#3399cc'
            }
        })
        
    except Exception as e:
        print(f"❌ Payment order creation failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)