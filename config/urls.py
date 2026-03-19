"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from analyzer import views
from django.contrib import admin
from django.urls import path
from analyzer.views import landing, analyze, signup, login_view, logout_view, history, delete_report, profile, upgrade, upgrade_to_pro, create_payment_order, payment_success, payment_failure

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('analyze/', analyze, name='analyze'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('history/', history, name='history'),
    path('profile/', profile, name='profile'),
    path('delete-report/<int:report_id>/', delete_report, name='delete_report'),
    path('upgrade/', upgrade, name='upgrade'),
    path('upgrade-to-pro/', upgrade_to_pro, name='upgrade_to_pro'),
    path('create-payment-order/', create_payment_order, name='create_payment_order'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-failure/', payment_failure, name='payment_failure'),
]
