#!/usr/bin/env python3
"""
ULTIMATE GUNICORN STARTUP SCRIPT
This script completely bypasses any render.yaml issues
"""

import os
import sys
import subprocess

def main():
    """Main startup function"""
    
    print("🚀 ULTIMATE GUNICORN STARTUP")
    print("=" * 50)
    
    # Set up Python path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.absolute_minimal_settings')
    print(f"⚙️ Django settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    
    # Test Django import
    try:
        import django
        print(f"✅ Django {django.get_version()} imported")
    except Exception as e:
        print(f"❌ Django import failed: {e}")
        return False
    
    # Test Django setup
    try:
        django.setup()
        print("✅ Django setup successful")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False
    
    # Test WSGI application
    try:
        from config.minimal_wsgi import application
        print("✅ WSGI application loaded")
    except Exception as e:
        print(f"❌ WSGI application failed: {e}")
        return False
    
    # Get port
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Port: {port}")
    
    # Start Gunicorn
    print("🚀 Starting Gunicorn...")
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        'config.minimal_wsgi:application'
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed: {e}")
        return False
    except KeyboardInterrupt:
        print("👋 Gunicorn stopped")
        return True
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    else:
        print("✅ Gunicorn started successfully")
