# 🚀 Deployment Guide for Developer Portfolio Analyzer

## 📋 Prerequisites

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub Repository** - Push your code to GitHub
3. **API Keys** - Get your API keys ready

## 🔧 Step 1: Update Environment Variables

### In Render Dashboard, set these environment variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://... (automatically set by Render)
OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token (optional)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_SECRET=your-razorpay-secret-key
ALLOWED_HOSTS=your-app-name.onrender.com
```

## 📦 Step 2: Deploy to Render

### Option 1: Using render.yaml (Recommended)
1. Push your code to GitHub
2. Go to Render Dashboard
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect your render.yaml

### Option 2: Manual Setup
1. **Web Service**:
   - Name: devportfolio
   - Environment: Python
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

2. **PostgreSQL Database**:
   - Name: devportfolio-db
   - Database Name: portfolio_analyzer
   - User: devportfolio

## 🔑 Step 3: Configure API Keys

### OpenAI API Key
1. Go to [OpenAI Dashboard](https://platform.openai.com/)
2. Get your API key
3. Add to Render environment variables

### Razorpay Keys
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Get your Test/Live keys
3. Add to Render environment variables

### GitHub Token (Optional)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token
3. Add to Render environment variables

## 🛠️ Step 4: Update Razorpay Settings

### For Production:
```python
# In config/settings.py
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_SECRET = os.getenv('RAZORPAY_SECRET')
```

### Update ALLOWED_HOSTS:
```python
ALLOWED_HOSTS = ["your-app-name.onrender.com"]
```

## 🧪 Step 5: Test Your Deployment

1. **Health Check**: Visit `https://your-app-name.onrender.com/`
2. **Signup**: Create a new account
3. **Login**: Test login functionality
4. **Payment**: Test upgrade to Pro (use test cards)
5. **Analysis**: Test GitHub portfolio analysis

## 🎯 Test Cards for Razorpay

### Successful Payment:
- Card: `4111 1111 1111 1111`
- Expiry: Any future date
- CVV: Any 3 digits
- OTP: `123456`

### Failed Payment:
- Card: `4111 1111 1111 1110`

## 📁 File Structure

```
portfolio-analyzer/
├── config/
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── analyzer/
│   ├── views.py             # Django views
│   ├── models.py            # Database models
│   ├── templates/           # HTML templates
│   └── static/              # CSS/JS files
├── build.sh                 # Build script
├── Procfile                 # Process configuration
├── requirements.txt         # Python packages
├── render.yaml             # Render configuration
└── .env.example            # Environment variables template
```

## 🔍 Troubleshooting

### Common Issues:

1. **500 Error - ALLOWED_HOSTS**
   ```python
   ALLOWED_HOSTS = ["your-app-name.onrender.com"]
   ```

2. **Database Connection Error**
   - Check DATABASE_URL in environment variables
   - Ensure PostgreSQL database is running

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic --noinput`
   - Check STATIC_ROOT setting

4. **Payment Not Working**
   - Verify Razorpay keys in environment variables
   - Check if keys are test or live mode

5. **OpenAI API Error**
   - Verify OPENAI_API_KEY in environment variables
   - Check API key credits

## 🚀 Production Checklist

- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Set DEBUG=False
- [ ] Configure all API keys
- [ ] Test payment flow
- [ ] Test user authentication
- [ ] Verify static files are loading
- [ ] Set up custom domain (optional)
- [ ] Configure SSL (automatic on Render)

## 📞 Support

If you encounter issues:

1. Check Render logs
2. Verify environment variables
3. Test locally with same settings
4. Check API key validity

---

**🎉 Your SaaS is ready for production!**

**Deploy now and start accepting real payments! 💰**
