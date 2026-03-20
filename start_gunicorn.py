#!/usr/bin/env python3
"""
ULTIMATE STARTUP SCRIPT - Bypass all Render issues
This script completely bypasses any render.yaml caching problems
"""
import os
import sys
import subprocess

def main():
    """Main startup function with comprehensive error handling"""
    
    print("🚀 ULTIMATE GUNICORN STARTUP - Render Deployment Fix")
    print("=" * 60)
    
    # Debug information
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"� Python path: {sys.path}")
    
    # Set environment variables explicitly
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.absolute_minimal_settings')
    print(f"⚙️ Django settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    
    # Add current directory to Python path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
        print("📂 Added current directory to Python path")
    
    # Test Django setup
    try:
        import django
        print(f"✅ Django {django.get_version()} imported")
        
        django.setup()
        print("✅ Django setup successful")
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        print("🔧 Attempting fallback...")
        
        # Fallback: try to import minimal settings directly
        try:
            from config import absolute_minimal_settings
            print("✅ Minimal settings imported directly")
        except Exception as fallback_error:
            print(f"❌ Fallback failed: {fallback_error}")
            return False
    
    # Test WSGI application
    try:
        from config.minimal_wsgi import application
        print("✅ WSGI application loaded")
        
        # Test the application
        print("🧪 Testing WSGI application...")
        if hasattr(application, '__call__'):
            print("✅ WSGI application is callable")
        else:
            print("❌ WSGI application is not callable")
            return False
            
    except Exception as e:
        print(f"❌ WSGI application failed: {e}")
        print("🔧 Attempting to create WSGI application manually...")
        
        # Fallback: create WSGI application manually
        try:
            from django.core.wsgi import get_wsgi_application
            application = get_wsgi_application()
            print("✅ Manual WSGI application created")
        except Exception as wsgi_error:
            print(f"❌ Manual WSGI creation failed: {wsgi_error}")
            return False
    
    # Get port
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Port: {port}")
    
    # Build Gunicorn command
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '120',
        '--keepalive', '5',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        'config.minimal_wsgi:application'
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    print("=" * 60)
    print("🚀 Starting Gunicorn...")
    
    # Start Gunicorn
    try:
        subprocess.run(cmd, check=True)
        print("✅ Gunicorn started successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Gunicorn not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'], check=True)
        print("� Gunicorn installed. Retrying...")
        subprocess.run(cmd, check=True)
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    else:
        print("✅ Gunicorn started successfully")
