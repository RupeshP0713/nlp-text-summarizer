# NLP Text Summarizer (Django)

This project is now a Django web app with a modern UI similar to your reference screenshots:
- paragraph/bullet modes
- summary length slider
- auto keyword chips
- copy/save actions
- light/dark theme

## Backend Design (Strong + Modular)

The backend is separated into clear layers:
- `summarizer/forms.py`: strict request validation and limits
- `summarizer/services.py`: summarization service logic (no HTTP code)
- `summarizer/views.py`: API endpoints + JSON error handling
- `app/core/nlp_engine.py`: NLP ranking engine (PageRank-based extraction)

Security-focused defaults in `config/settings.py`:
- CSRF middleware enabled for all POST requests
- `HttpOnly` session and CSRF cookies
- clickjacking and MIME sniffing protections
- configurable `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` from environment

## Tech Stack

- Django
- NLTK
- NumPy
- NetworkX
- SciPy

## Quick Start (Windows PowerShell)

```powershell
cd "C:\Project\nlp-text-summarizer"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r req.txt
python manage.py migrate
python manage.py runserver
```

Open: `http://127.0.0.1:8000`

## API Endpoints

- `POST /api/summarize/`
  - body: `text`, `mode` (`paragraph|bullet`), `length_ratio`, `keywords`
- `POST /api/keywords/`
  - body: `text`

Both endpoints return JSON and validation errors with HTTP 400.

## Project Structure

```text
nlp-text-summarizer/
|-- app/core/nlp_engine.py
|-- config/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- summarizer/
|   |-- forms.py
|   |-- services.py
|   |-- urls.py
|   `-- views.py
|-- templates/summarizer/index.html
|-- static/summarizer/css/styles.css
|-- static/summarizer/js/app.js
|-- manage.py
`-- req.txt
```

## Optional Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`1` or `0`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated)
