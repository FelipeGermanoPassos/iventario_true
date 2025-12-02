# Vercel entrypoint for the Flask app
# Exports a WSGI-compatible `app` object

from app import create_app

app = create_app()
