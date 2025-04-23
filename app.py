# Filename: app.py

import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

# Get the directory where app.py is located
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/riot.txt')
def serve_riot_txt():
  """
  Serves the physical riot.txt file from the application's root directory.
  """
  try:
    # Serve the file named 'riot.txt' from the app's root directory ('.')
    # Explicitly set the mimetype to text/plain
    return send_from_directory(
        directory=APP_ROOT,
        path='riot.txt', # Changed from 'filename' to 'path' for Flask >= 2.0
        mimetype='text/plain'
    )
  except FileNotFoundError:
    # If riot.txt doesn't exist, return a 404 error
    abort(404, description="riot.txt not found.")

@app.route('/')
def home():
    """
    Simple homepage to confirm the app is running.
    Provides instructions if riot.txt is missing.
    """
    riot_file_path = os.path.join(APP_ROOT, 'riot.txt')
    if os.path.exists(riot_file_path):
        return "Flask app is running. Visit /riot.txt to see the verification file."
    else:
        return "Flask app is running, but <strong>riot.txt</strong> is missing from the project directory!"

# Note: No app.run() here. Gunicorn will run the app in production.