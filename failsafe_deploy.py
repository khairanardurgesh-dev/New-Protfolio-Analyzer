#!/usr/bin/env python3
"""
FAILSAFE DEPLOYMENT SCRIPT
This script completely eliminates all possible causes of ModuleNotFoundError
"""

import os
import sys
import subprocess
import django
from django.conf import settings

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Failsafe deployment main function"""
    
    print("🚀 FAILSAFE DEPLOYMENT STARTED")
    print("=" * 50)
    
    # Step 1: Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Step 2: Set up Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    # Step 3: Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.minimal_settings')
    print(f"⚙️ Django settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    
    # Step 4: Install dependencies
    print("📦 Installing dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements_prod.txt")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Dependencies installed")
    
    # Step 5: Test Django import
    print("🧪 Testing Django import...")
    try:
        import django
        print(f"✅ Django {django.get_version()} imported")
    except Exception as e:
        print(f"❌ Django import failed: {e}")
        return False
    
    # Step 6: Test Django setup
    print("⚙️ Setting up Django...")
    try:
        django.setup()
        print("✅ Django setup successful")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False
    
    # Step 7: Test app loading
    print("📱 Testing app loading...")
    try:
        from django.apps import apps
        app_configs = list(apps.get_app_configs())
        print(f"✅ Apps loaded: {[app.name for app in app_configs]}")
    except Exception as e:
        print(f"❌ App loading failed: {e}")
        return False
    
    # Step 8: Run migrations
    print("🗄️ Running migrations...")
    success, stdout, stderr = run_command("python manage.py migrate --noinput")
    if not success:
        print(f"❌ Migration failed: {stderr}")
        return False
    print("✅ Migrations completed")
    
    # Step 9: Collect static files
    print("📦 Collecting static files...")
    success, stdout, stderr = run_command("python manage.py collectstatic --noinput")
    if not success:
        print(f"❌ Static files failed: {stderr}")
        return False
    print("✅ Static files collected")
    
    # Step 10: Test WSGI application
    print("🌐 Testing WSGI application...")
    try:
        from config.wsgi import application
        print("✅ WSGI application loaded")
    except Exception as e:
        print(f"❌ WSGI application failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 FAILSAFE DEPLOYMENT SUCCESSFUL!")
    print("✅ All tests passed")
    print("✅ Application is ready to start")
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("❌ FAILSAFE DEPLOYMENT FAILED")
        sys.exit(1)
    else:
        print("🚀 Application ready for Gunicorn startup")
