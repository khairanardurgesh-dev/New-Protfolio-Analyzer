# DevPortfolio Analyzer

AI-powered GitHub portfolio analyzer that helps developers understand their strengths, weaknesses, and career opportunities.

## Features

- **Portfolio Analysis**: Comprehensive scoring system (0-100) based on GitHub activity
- **AI Career Advice**: Personalized recommendations powered by OpenAI
- **Skill Insights**: Language distribution and technical expertise analysis
- **Report History**: Track progress over time with saved analyses
- **PDF Export**: Download detailed reports for sharing
- **Modern UI**: Responsive design with Tailwind CSS
- **User Authentication**: Secure login/signup system

## Tech Stack

- **Backend**: Django 4.2.7
- **Frontend**: Tailwind CSS, vanilla JavaScript
- **Database**: PostgreSQL (production), SQLite (development)
- **AI**: OpenAI GPT-3.5-turbo
- **PDF Generation**: ReportLab
- **Deployment**: Render

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- OpenAI API key (optional, fallback advice available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to see the application.

## Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://username:password@localhost:5432/portfolio_analyzer
OPENAI_API_KEY=your-openai-api-key-here
GITHUB_TOKEN=your-github-token-here
```

## Deployment

### Render (Recommended)

1. **Connect your GitHub repository** to Render
2. **Use the provided `render.yaml`** configuration
3. **Set environment variables** in the Render dashboard:
   - `SECRET_KEY`: Generate a secure key
   - `DATABASE_URL`: Auto-provided by Render
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ALLOWED_HOSTS`: Your Render domain
4. **Deploy** - Render will automatically build and deploy

### Manual Deployment

1. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set production settings**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings_production
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

## API Usage

### GitHub Analysis Endpoint

```bash
POST /analyze/
Content-Type: application/x-www-form-urlencoded

username=octocat
```

### PDF Download

```bash
GET /download-pdf/
```

Requires a valid session with recent analysis data.

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 guidelines. Use tools like `flake8` or `black` for formatting.

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Make changes** following existing patterns
3. **Test thoroughly**
4. **Submit pull request**

## Architecture

```
portfolio-analyzer/
├── analyzer/                 # Main Django app
│   ├── views.py              # View logic
│   ├── models.py             # Database models
│   ├── github_service.py     # GitHub API integration
│   ├── portfolio_analyzer.py # Analysis logic
│   ├── ai_report.py          # OpenAI integration
│   └── templates/            # HTML templates
├── config/                   # Django project settings
│   ├── settings.py          # Development settings
│   ├── settings_production.py # Production settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploaded files
├── requirements.txt          # Python dependencies
├── Procfile                 # Process configuration
├── render.yaml              # Render deployment config
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Roadmap

- [ ] GitHub OAuth integration
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Multi-language support

---

**Built with ❤️ for the developer community**
