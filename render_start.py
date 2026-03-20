#!/usr/bin/env python3
"""
Render startup script that handles all potential import issues
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def main():
    """Main startup function for Render deployment"""
    
    print("🚀 Starting Django application on Render...")
    
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        # Setup Django
        print("⚙️ Setting up Django...")
        django.setup()
        print("✅ Django setup successful")
        
        # Run migrations
        print("🗄️ Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed")
        
        # Collect static files
        print("📦 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
        
        print("🎉 Django application is ready!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
