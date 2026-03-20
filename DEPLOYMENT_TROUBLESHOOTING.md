# 🔧 Deployment Troubleshooting Guide

## 🚨 Current Issues

### **Issue 1: Git Remote Points to Placeholder**
**Problem**: `fatal: repository 'https://github.com/YOUR_USERNAME/YOUR_REPO.git/' not found`

**Solution**:
```bash
# Remove the placeholder remote
git remote remove origin

# Add your actual repository
git remote add origin https://github.com/YOUR_ACTUAL_USERNAME/YOUR_ACTUAL_REPO.git

# Push to main
git push -u origin main
```

### **Issue 2: ModuleNotFoundError: No module named 'app'**
**Problem**: This error typically occurs when:
1. Wrong import statements in Python files
2. Missing app configuration
3. Incorrect PYTHONPATH setup
4. Render environment differences

**Solutions**:

#### **Solution A: Check Imports**
```python
# Check all imports in your files
# Look for: import app
# Should be: from analyzer import views
```

#### **Solution B: Verify App Configuration**
```python
# In config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analyzer',  # Make sure this is correct
]
```

#### **Solution C: Update build.sh**
```bash
#!/usr/bin/env bash

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

#### **Solution D: Update Procfile**
```bash
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --access-logfile -
```

## 🔍 Debugging Steps

### **Step 1: Local Testing**
```bash
# Test locally first
python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py migrate
```

### **Step 2: Check Dependencies**
```bash
# Verify all packages
pip freeze | grep -E "(django|gunicorn|whitenoise|psycopg2|razorpay)"
```

### **Step 3: Validate Configuration**
```bash
# Run validation script
python validate_build.py
```

## 🚀 Fixed Deployment Files

### **Updated build.sh**
```bash
#!/usr/bin/env bash
set -e  # Exit on any error

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running migrations..."
python manage.py migrate

echo "✅ Build completed successfully!"
```

### **Updated Procfile**
```bash
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --access-logfile - --error-logfile -
```

### **Updated render.yaml**
```yaml
services:
  - type: web
    name: devportfolio
    env: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
    healthCheckPath: /
    autoDeploy: true
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: DATABASE_URL
        fromDatabase:
          name: devportfolio-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: RAZORPAY_KEY_ID
        sync: false
      - key: RAZORPAY_SECRET
        sync: false
      - key: ALLOWED_HOSTS
        value: devportfolio.onrender.com
```

## 🎯 Common Render Issues & Solutions

### **Issue: Build Timeout**
**Solution**: Add `set -e` to build.sh and optimize requirements

### **Issue: Database Connection**
**Solution**: Ensure DATABASE_URL is set correctly in Render dashboard

### **Issue: Static Files 404**
**Solution**: Verify STATIC_ROOT and WhiteNoise middleware

### **Issue: Import Errors**
**Solution**: Check PYTHONPATH and app configuration

## 📋 Pre-Deployment Checklist

- [ ] Git remote points to actual repository
- [ ] All imports are correct
- [ ] Environment variables documented
- [ ] Build script tested locally
- [ ] Django check --deploy passes
- [ ] Static files collect successfully
- [ ] Migrations run without errors

## 🚀 Deployment Commands

### **Step 1: Fix Git Remote**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### **Step 2: Push Changes**
```bash
git add .
git commit -m "Fix deployment issues"
git push -u origin main
```

### **Step 3: Deploy on Render**
1. Go to Render dashboard
2. Connect your GitHub repository
3. Set environment variables
4. Deploy

---

## 🔍 If Issues Persist

### **Check Render Logs**
1. Go to your service dashboard
2. Click on "Logs" tab
3. Look for specific error messages
4. Search for "ModuleNotFoundError"

### **Check Build Logs**
1. Go to "Events" tab in Render
2. Find failed build
3. Click on build to see full log
4. Identify the exact error

### **Common Error Patterns**
```
ModuleNotFoundError: No module named 'app'
ImportError: cannot import name 'app'
django.core.exceptions.ImproperlyConfigured
```

---

## 🎉 Success Indicators

### **Your Deployment is Successful When:**
- ✅ Build completes without errors
- ✅ Health check passes
- ✅ Application loads in browser
- ✅ Login/signup works
- ✅ GitHub analysis works
- ✅ Payment flow works

---

**🚀 Follow this guide to resolve deployment issues!**
