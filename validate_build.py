#!/usr/bin/env python
"""
Build Validation Script for Developer Portfolio Analyzer
Validates deployment readiness and identifies potential issues
"""

import os
import sys
import subprocess
import django
from django.conf import settings

def run_command(cmd):
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        ('django', 'Django'),
        ('whitenoise', 'WhiteNoise'),
        ('gunicorn', 'Gunicorn'),
        ('dj_database_url', 'dj-database-url'),
        ('psycopg2', 'psycopg2-binary'),
        ('razorpay', 'Razorpay'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_good = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_django_settings():
    """Check Django configuration"""
    print("\n🔍 Checking Django configuration...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        checks = [
            ('DEBUG', settings.DEBUG, False),
            ('ALLOWED_HOSTS', settings.ALLOWED_HOSTS, list),
            ('STATIC_URL', settings.STATIC_URL, str),
            ('STATIC_ROOT', getattr(settings, 'STATIC_ROOT', None), str),
            ('WhiteNoise middleware', 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE, bool),
            ('Analyzer app', 'analyzer' in settings.INSTALLED_APPS, bool),
        ]
        
        all_good = True
        for name, value, expected_type in checks:
            if value is None:
                print(f"  ❌ {name} - NOT SET")
                all_good = False
            elif expected_type == bool and not value:
                print(f"  ❌ {name} - INCORRECT")
                all_good = False
            elif expected_type == list and not isinstance(value, list):
                print(f"  ❌ {name} - WRONG TYPE")
                all_good = False
            else:
                print(f"  ✅ {name}")
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Django setup failed: {e}")
        return False

def check_build_commands():
    """Test build commands"""
    print("\n🔍 Testing build commands...")
    
    commands = [
        ('collectstatic', 'python manage.py collectstatic --noinput'),
        ('check', 'python manage.py check --deploy'),
    ]
    
    all_good = True
    for name, cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - FAILED")
            if stderr:
                print(f"     Error: {stderr.strip()}")
            all_good = False
    
    return all_good

def check_file_structure():
    """Check required files exist"""
    print("\n🔍 Checking file structure...")
    
    required_files = [
        'manage.py',
        'config/settings.py',
        'config/urls.py',
        'config/wsgi.py',
        'analyzer/views.py',
        'analyzer/models.py',
        'build.sh',
        'Procfile',
        'requirements_prod.txt',
        'render.yaml',
        '.env.example',
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("🚀 Developer Portfolio Analyzer - Build Validation")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ('Dependencies', check_dependencies),
        ('Django Settings', check_django_settings),
        ('Build Commands', check_build_commands),
        ('File Structure', check_file_structure),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 BUILD IS READY FOR DEPLOYMENT!")
        print("\n📋 Next steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Deploy on Render")
        print("3. Set environment variables")
        print("4. Test the application")
        return 0
    else:
        print("⚠️  BUILD NEEDS ATTENTION")
        print("Fix the failed checks before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
