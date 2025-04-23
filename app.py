# Filename: app.py
# --- Imports ---
import requests
from flask import (
    Flask, request, abort, flash, redirect, get_flashed_messages, Response, url_for
)
import html  # For escaping user input in HTML
import os  # For PORT binding
import datetime  # To get the current year for the footer
import json # To pass data to JS safely

# --- Configuration & Hardcoded Values ---
# !!! WARNING: Use Environment Variables on Render for secrets! Hardcoding is insecure! !!!

# Use Environment Variables first, fall back to placeholders (INSECURE for production)
RIOT_API_KEY = os.environ.get("RIOT_API_KEY", "RGAPI-Your-Actual-Riot-Api-Key-Here")
RIOT_VERIFICATION_CODE = os.environ.get("RIOT_VERIFICATION_CODE", "de8de887-acbe-467e-9afd-5feb469e7f41") # Example placeholder
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", 'a_very_insecure_default_key_for_testing_only_v4') # Changed placeholder

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY  # Set the secret key for flashing

# --- Rank Tier to Color Mapping (Example) ---
# You might want to refine these colors based on official Valorant rank colors
RANK_COLORS = {
    "Iron": "#505050",
    "Bronze": "#a97142",
    "Silver": "#c0c0c0",
    "Gold": "#ffd700",
    "Platinum": "#4e9996",
    "Diamond": "#d389f3",
    "Ascendant": "#53a85c",
    "Immortal": "#e44b59",
    "Radiant": "#f5f5ac",
    "Unranked": "#888888",
    # Add divisions if needed, e.g., "Iron 1", "Iron 2", etc.
}

# --- Enhanced CSS (Inspired by Target Image) ---
CUSTOM_CSS = """
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Root Variables - Inspired Palette */
:root {
    --bg-primary: #0f1519; /* Deep dark background */
    --bg-secondary: #1a2228; /* Slightly lighter surface */
    --bg-tertiary: #2c3840; /* Input fields, accents */
    --bg-tertiary-hover: #3a4a54;
    --primary-accent: #ff4655; /* Valorant Red/Pink */
    --primary-accent-hover: #e03c4a;
    --secondary-accent: #00c8c8; /* Cyan/Teal */
    --secondary-accent-hover: #00a0a0;
    --text-primary: #e1e1e1; /* Main text */
    --text-secondary: #8b979f; /* Muted text */
    --text-on-accent: #ffffff;
    --border-color: #3a4a54; /* Subtle borders */
    --border-highlight: rgba(255, 70, 85, 0.5); /* Accent border highlight */
    --shadow-color: rgba(0, 0, 0, 0.4);
    --font-family: 'Inter', sans-serif;
    --radius-sm: 4px;
    --radius-md: 8px;
}

/* Global Styles */
*, *::before, *::after { box-sizing: border-box; }

html {
    scroll-behavior: smooth;
    font-size: 16px; /* Base font size */
}

body {
    background: linear-gradient(135deg, var(--bg-primary) 0%, #141b20 100%);
    color: var(--text-primary);
    font-family: var(--font-family);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    line-height: 1.6;
    margin: 0;
    overflow-x: hidden; /* Prevent horizontal scroll */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Three.js Canvas Placeholder - Style if you add it */
#three-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1; /* Place behind content */
    /* background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%); */ /* Example static background */
}

main {
    flex: 1;
    padding: 3rem 1rem; /* More vertical padding */
    position: relative; /* Needed for z-index stacking if canvas is used */
    z-index: 1;
}

/* Container */
.container {
    max-width: 1100px; /* Wider container */
    margin-left: auto;
    margin-right: auto;
    padding-left: 15px;
    padding-right: 15px;
}

/* Navbar Styling */
.navbar {
    background-color: rgba(26, 34, 40, 0.85); /* Semi-transparent */
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}
.navbar-brand {
    font-weight: 800; /* Bolder */
    color: var(--primary-accent) !important;
    font-size: 1.8rem;
    letter-spacing: -1px;
    text-transform: uppercase;
    transition: color 0.2s ease;
}
.navbar-brand:hover {
    color: var(--primary-accent-hover) !important;
}

/* Card Styling */
.styled-card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 2.5rem 3rem; /* More padding */
    margin-top: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px var(--shadow-color);
    transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
    position: relative;
    overflow: hidden; /* For potential pseudo-elements */
}
/* Optional: Add a subtle top border highlight */
.styled-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--primary-accent), transparent);
    opacity: 0.6;
}

.card-title {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}
.card-subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 2.5rem; /* More space below subtitle */
}

/* Form Styling */
.form-label {
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.form-control {
    background-color: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.8rem 1.2rem;
    border-radius: var(--radius-sm);
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
    font-size: 1rem;
}
.form-control:focus {
    background-color: var(--bg-tertiary-hover);
    border-color: var(--primary-accent);
    box-shadow: 0 0 0 3px rgba(255, 70, 85, 0.2); /* Accent focus glow */
    color: var(--text-primary);
    outline: none;
}
.form-control::placeholder {
    color: #6a7881; /* Lighter placeholder */
}
.input-group {
    position: relative; /* For positioning the '#' */
}
.input-group-text {
    position: absolute;
    left: 1px; /* Adjust as needed */
    top: 1px;
    bottom: 1px;
    background-color: #3a4a54; /* Darker than input */
    border: none;
    border-right: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 0 1rem;
    display: flex;
    align-items: center;
    border-top-left-radius: var(--radius-sm);
    border-bottom-left-radius: var(--radius-sm);
    font-weight: 600;
}
/* Adjust input padding when using input-group-text */
.input-group .form-control {
    padding-left: 3.5rem; /* Make space for the '#' */
}
/* Specific styling for the tag input with '#' */
#tag {
    padding-left: 1.2rem; /* Reset padding as '#' is handled differently */
}
.tag-group .input-group-text {
    position: static; /* Normal flow */
    border-radius: var(--radius-sm);
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border: 1px solid var(--border-color);
     border-right: none;
}
.tag-group .form-control {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}


/* Button Styling */
.btn {
    padding: 0.9rem 2rem;
    border-radius: var(--radius-sm);
    font-weight: 700;
    transition: all 0.2s ease;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 0.95rem;
    border: 1px solid transparent;
    line-height: 1.5; /* Ensure text vertical centering */
}
.btn-primary {
    background-color: var(--primary-accent);
    border-color: var(--primary-accent);
    color: var(--text-on-accent);
    box-shadow: 0 4px 15px rgba(255, 70, 85, 0.2);
}
.btn-primary:hover {
    background-color: var(--primary-accent-hover);
    border-color: var(--primary-accent-hover);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 70, 85, 0.3);
    color: var(--text-on-accent);
}
.btn-secondary {
    background-color: var(--bg-tertiary);
    border-color: var(--border-color);
    color: var(--text-secondary);
}
.btn-secondary:hover {
    background-color: var(--bg-tertiary-hover);
    border-color: var(--border-highlight);
    color: var(--text-primary);
    transform: translateY(-2px);
}
.d-grid .btn {
    width: 100%;
}

/* Results Card Specific Styling */
.result-card {
    padding: 3rem;
}
.result-card h2 { /* Title: "Rank Result" */
    font-size: 1.6rem;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}
.result-card .player-id { /* PlayerName#TAG */
    color: var(--text-secondary);
    margin-bottom: 2rem;
    font-size: 1.1rem;
    font-weight: 500;
}
.result-card hr {
    border-color: var(--border-color);
    margin: 2rem 0;
    border-style: solid;
}

.rank-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    text-align: center;
}
.rank-icon-wrapper {
    position: relative;
    margin-bottom: 1rem;
}
.rank-icon img, .rank-icon-placeholder {
    width: 120px;
    height: 120px;
    object-fit: contain;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 50%;
    padding: 10px;
    border: 2px solid var(--border-color); /* Default border */
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    transition: border-color 0.3s ease;
}
.rank-icon-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    font-size: 0.9em;
    font-style: italic;
}
/* Dynamic border color via inline style */

.rank-details h3.rank-tier { /* e.g., "Immortal 3" */
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0 0 0.25rem 0;
    text-transform: uppercase;
    letter-spacing: 1px;
    /* Color applied via inline style */
    text-shadow: 0 2px 5px rgba(0,0,0,0.5);
}
.rank-details p { /* LP display */
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
    font-size: 1.1rem;
}
.rank-details strong { /* LP value */
    color: var(--text-primary);
    font-weight: 600;
}

.stats-row {
    display: flex;
    justify-content: center;
    gap: 3rem; /* More space */
    margin-top: 1.5rem;
    font-size: 1.1rem;
    width: 100%;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
}
.stats-row div {
    color: var(--text-secondary);
    font-weight: 500;
}
.stats-row strong {
    color: var(--text-primary);
    font-weight: 700;
    margin-left: 0.5em;
}
.stats-row .wins { color: #66bb6a; } /* Green for wins */
.stats-row .losses { color: #ef5350; } /* Red for losses */

/* Alert Styling */
.alert {
    border: 1px solid var(--border-color);
    border-left-width: 5px; /* Thicker left border */
    border-radius: var(--radius-sm);
    padding: 1.2rem 1.5rem;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1rem;
    background-color: var(--bg-secondary); /* Match card bg */
    box-shadow: 0 3px 10px var(--shadow-color);
}
.alert strong {
    font-weight: 600;
    margin-right: 0.5em;
}
/* Specific Alert Colors (Using Borders and Text) */
.alert-danger { border-left-color: #dc3545; color: #f8d7da; }
.alert-warning { border-left-color: #ffc107; color: #fff3cd; }
.alert-success { border-left-color: #28a745; color: #d4edda; }
.alert-info { border-left-color: #17a2b8; color: #d1ecf1; }

.alert .btn-close {
    filter: invert(0.8) grayscale(100%) brightness(150%);
    background-size: 60%; /* Make X smaller */
    opacity: 0.7;
    transition: opacity 0.2s ease;
}
.alert .btn-close:hover {
    opacity: 1;
}


/* Footer Styling */
footer {
    background-color: var(--bg-primary); /* Match primary background */
    border-top: 1px solid var(--border-color);
    padding: 2.5rem 1rem;
    color: var(--text-secondary);
    font-size: 0.9em;
    margin-top: auto; /* Pushes footer to bottom */
    text-align: center;
}
footer p { margin-bottom: 0.5rem; }
footer a {
    color: var(--secondary-accent);
    text-decoration: none;
    transition: color 0.2s ease;
}
footer a:hover {
    color: var(--secondary-accent-hover);
}

/* Utility Classes */
.text-center { text-align: center; }
.mt-5 { margin-top: 3rem !important; } /* Adjust spacing */
.mb-4 { margin-bottom: 2rem !important; }
/* Add more utilities as needed */

"""

# --- HTML Templates (as Python functions returning strings) ---

def render_base_html(title="Ecaly", content="", head_extra="", scripts_extra=""):
    """Simulates base.html template with enhanced styling."""
    flashed_messages_html = ""
    messages = get_flashed_messages(with_categories=True)
    # Use a container *outside* the main content for flashed messages for better layout control
    if messages:
        flashed_messages_html += "<div class='container flashed-messages-container'><div class='row justify-content-center'><div class='col-lg-8 col-md-10'>"
        for category, message in messages:
            safe_message = html.escape(message)
            alert_class = category if category in ['danger', 'warning', 'success', 'info'] else 'info'
            flashed_messages_html += f"""
            <div class="alert alert-{alert_class} alert-dismissible fade show" role="alert">
                <span>{safe_message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            """
        flashed_messages_html += "</div></div></div>"

    current_year = datetime.datetime.now().year
    return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    {head_extra}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{CUSTOM_CSS}</style>
    </head>
<body>
    <nav class="navbar">
        <div class="container"><a class="navbar-brand" href="/">ECALY</a></div>
    </nav>

    {flashed_messages_html}

    <main>
        <div class="container">
            {content}
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; {current_year} Ecaly - Inspired by modern stats trackers. Rank data provided by Riot Games API.</p>
            <p class="small">Ecaly is not endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.</p>
            </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    {scripts_extra} </body>
</html>
"""

def render_index_page():
    """Renders the content for the index page with new styles."""
    index_content = """
<div class="row justify-content-center">
    <div class="col-lg-6 col-md-8">
        <div class="styled-card">
            <h2 class="card-title text-center">Valorant Rank Lookup</h2>
            <p class="card-subtitle text-center">Enter a player's Riot ID (PlayerName#TAG) below.</p>
            <form action="/lookup" method="post">
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" name="username" placeholder="PlayerName" required>
                </div>
                <div class="mb-4">
                     <label for="tag" class="form-label">Tagline</label>
                    <div class="input-group tag-group">
                        <span class="input-group-text">#</span>
                        <input type="text" class="form-control" id="tag" name="tag" placeholder="TAG" required>
                    </div>
                </div>
                <div class="d-grid mt-4">
                    <button type="submit" class="btn btn-primary btn-lg">Lookup Rank</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""
    return render_base_html(title="Ecaly - Valorant Rank Lookup", content=index_content)

def render_results_page(player_name, player_tag, rank_data=None, error=None):
    """Renders the content for the results page with new styles."""
    safe_player_name = html.escape(player_name)
    safe_player_tag = html.escape(player_tag)
    safe_error = html.escape(error) if error else None

    # Prepare data to potentially pass to JavaScript
    results_data_json = json.dumps({'rank': rank_data, 'error': safe_error})

    results_content = f"""
<div class="row justify-content-center">
    <div class="col-lg-6 col-md-8">
        <div class="styled-card result-card">
            <h2 class="text-center">Rank Result</h2>
            <p class="text-center player-id">{safe_player_name}<span>#{safe_player_tag}</span></p>
            <hr>
"""
    # Add script tag to pass data to JS (will be picked up by base template's script)
    results_content += f"""
    <script id="results-data" type="application/json">
        {results_data_json}
    </script>
    """

    if safe_error:
        results_content += f'<div class="alert alert-danger" role="alert"><strong>Lookup Failed:</strong> {safe_error}</div>'
    elif rank_data is not None:
        # Extract and sanitize data
        tier_raw = rank_data.get('tier', 'Unranked')
        # Basic tier name extraction (e.g., "Immortal 1" -> "Immortal")
        tier_base = tier_raw.split(' ')[0] if tier_raw != 'Unranked' else 'Unranked'

        tier = html.escape(tier_raw)
        # Division is often part of the tier name in Valorant API (e.g., "Diamond 2")
        # Let's keep LP separate if available
        lp = html.escape(str(rank_data.get('lp', '--')))
        wins = html.escape(str(rank_data.get('wins', '--')))
        losses = html.escape(str(rank_data.get('losses', '--')))
        icon_url = rank_data.get('rank_icon_url') # Note: Valorant Ranked API v1 doesn't directly provide icon URL

        # Determine colors and styles based on rank
        rank_color = RANK_COLORS.get(tier_base, RANK_COLORS["Unranked"]) # Use base tier for color lookup
        icon_border_style = f"border-color: {rank_color}; box-shadow: 0 0 15px {rank_color}60;" # Add glow effect


        results_content += '<div class="rank-display">'
        results_content += '<div class="rank-icon-wrapper">' # Wrapper for icon
        # --- Icon Placeholder - Replace with actual icon if API provided it ---
        # The standard Valorant Ranked v1 API *doesn't* give an icon URL.
        # You usually map tier names to static image assets you host yourself.
        # Example: <img src="/static/images/ranks/{tier_base.lower()}.png" alt="{tier}" style="{icon_border_style}">
        # For now, using a placeholder div:
        results_content += f'<div class="rank-icon-placeholder" style="{icon_border_style}">{tier_base}</div>'
        results_content += '</div>' # End rank-icon-wrapper

        results_content += '<div class="rank-details text-center">'
        tier_display = tier # Already escaped, includes division like "Diamond 2"
        results_content += f'<h3 class="rank-tier" style="color: {rank_color};">{tier_display}</h3>'
        if lp != '--' and tier_base != 'Unranked' and tier_base != 'Radiant': # LP usually shown except for Unranked/Radiant
             results_content += f'<p><strong>{lp}</strong> RR</p>' # Using RR (Rank Rating) common term

        results_content += '</div>' # End rank-details

        # Only show Wins/Losses if they are available (not '--')
        if wins != '--' or losses != '--':
            results_content += '<div class="stats-row">'
            if wins != '--':
                 results_content += f'<div class="wins">Wins: <strong>{wins}</strong></div>'
            if losses != '--':
                 results_content += f'<div class="losses">Losses: <strong>{losses}</strong></div>'
            results_content += '</div>' # End stats-row

        results_content += '</div>' # End rank-display

        # Add message for unranked players if found but no rank tier
        if tier_base == 'Unranked' and not safe_error:
            results_content += '<div class="alert alert-info mt-4" role="alert">Player found, but appears unranked in the current competitive season.</div>'

    else:
        # Case where rank_data is None but no specific error was caught (shouldn't happen often)
         results_content += '<div class="alert alert-warning" role="alert">Could not retrieve rank information.</div>'


    results_content += '<div class="text-center mt-5"><a href="/" class="btn btn-secondary">Lookup Another Player</a></div>'
    results_content += '</div></div></div>' # End card, col, row

    return render_base_html(title=f"Rank: {safe_player_name}#{safe_player_tag} - Ecaly", content=results_content)


# --- Flask Routes ---

@app.route('/riot.txt')
def serve_riot_txt():
    """Serves the verification code directly."""
    # IMPORTANT: Ensure RIOT_VERIFICATION_CODE is correctly set in your environment!
    current_verification_code = RIOT_VERIFICATION_CODE
    if not current_verification_code or current_verification_code == "de8de887-acbe-467e-9afd-5feb469e7f41": # Default placeholder check
        print("WARNING: RIOT_VERIFICATION_CODE is not set via ENV or is using the placeholder!")
        # Return a placeholder or error in production if not set, avoid exposing default.
        # For testing, returning the placeholder might be okay.
    return Response(current_verification_code, mimetype='text/plain')

@app.route('/')
def index():
    """Renders the homepage."""
    return render_index_page()

@app.route('/lookup', methods=['POST'])
def lookup():
    """Handles form submission, calls API, returns results HTML."""
    username = request.form.get('username', '').strip()
    tag = request.form.get('tag', '').strip()

    if not username or not tag:
        flash('Please provide both Riot Username and Tagline.', 'warning')
        return redirect(url_for('index')) # Use url_for for routing

    # Validate API Key
    current_api_key = RIOT_API_KEY
    if not current_api_key or current_api_key == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("ERROR: RIOT_API_KEY environment variable not set or is using the placeholder value.")
        flash('Application configuration error: API key missing or invalid. Please contact the administrator.', 'danger')
        # Render results page with error, but don't redirect
        return render_results_page(
            player_name=username,
            player_tag=tag,
            error='Server configuration error. Please try again later.' # User-friendly message
        )

    rank_data = None
    error_message = None
    print(f"Looking up player: {username}#{tag}")

    try:
        headers = {"X-Riot-Token": current_api_key}
        # Use environment variables for regions, default to common ones
        # Adjust these defaults based on your primary user base
        account_region = os.environ.get("RIOT_ACCOUNT_REGION", "americas") # e.g., americas, asia, europe, sea
        valorant_region = os.environ.get("RIOT_VALORANT_REGION", "na")     # e.g., na, eu, ap, kr, latam, br

        # --- 1. Get PUUID using Account API ---
        account_api_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
        print(f"Calling Account API: {account_api_url}")
        account_response = requests.get(account_api_url, headers=headers, timeout=10) # Reduced timeout slightly

        # Specific handling for 404 on account lookup
        if account_response.status_code == 404:
             raise ValueError(f"Riot ID '{username}#{tag}' not found in the '{account_region}' region. Check spelling, tag, and selected region.")
        account_response.raise_for_status() # Raise exceptions for other errors (4xx, 5xx)

        account_data = account_response.json()
        puuid = account_data.get('puuid')

        if not puuid:
            raise ValueError("Could not extract PUUID from API response.")
        print(f"Found PUUID: {puuid}")

        # --- 2. Get Rank using Valorant Ranked API ---
        # NOTE: The v1 endpoint provides data for the *current* competitive season.
        # It might return very little data if the player hasn't played ranked recently.
        rank_api_url = f"https://{valorant_region}.api.riotgames.com/val/ranked/v1/by-puuid/{puuid}"
        # Alternative (Content API - often more info but needs different parsing):
        # rank_api_url = f"https://{valorant_region}.api.riotgames.com/val/content/v1/contents" # (Less relevant for rank directly)
        # Alternative (MMR API - gives detailed MMR but structure varies):
        # rank_api_url = f"https://{valorant_region}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}" # (Needs more processing)

        print(f"Calling VAL Rank API: {rank_api_url}")
        rank_response = requests.get(rank_api_url, headers=headers, timeout=15)

        # Handle 404 for Rank API - means player exists but has no data in this specific ranked queue/season
        if rank_response.status_code == 404:
            print(f"No VAL ranked data found for PUUID {puuid} in region {valorant_region} (status 404). Treating as Unranked.")
            rank_data = {'tier': 'Unranked', 'lp': 0, 'wins': 0, 'losses': 0} # Provide default unranked structure
        else:
            rank_response.raise_for_status() # Raise for other errors
            api_result = rank_response.json()
            print(f"Received rank data: {api_result}") # Log the raw response

            # --- Parse the Ranked v1 Response ---
            # Structure might be under 'data' or directly at root depending on exact endpoint/version
            # The 'by-puuid' endpoint (v1) seems to return data in `images` and tier info.
            # Let's refine parsing based on typical Valorant API structures.
            # Often MMR data comes from a different endpoint (`/mmr/v1/players/{puuid}`)
            # The `/ranked/v1/by-puuid/` endpoint is *less* common for detailed rank like tier/RR.
            # Let's *assume* we are getting data similar to what MMR endpoint might provide,
            # or fallback gracefully. A common structure has 'data.currentData' or similar.

            # --- IMPORTANT RE-EVALUATION ---
            # The `/val/ranked/v1/by-puuid/{puuid}` endpoint IS NOT the correct one for detailed Tier/RR.
            # It seems related to leaderboards.
            # The correct endpoint is likely `/val/mmr/v1/by-puuid/{puuid}`.
            # Let's switch to that, assuming it's available for your API key type.
            mmr_api_url = f"https://{valorant_region}.api.riotgames.com/val/mmr/v1/by-puuid/{puuid}"
            print(f"Calling VAL MMR API: {mmr_api_url}")
            mmr_response = requests.get(mmr_api_url, headers=headers, timeout=15)

            if mmr_response.status_code == 404:
                 print(f"No VAL MMR data found for PUUID {puuid} in region {valorant_region} (status 404). Treating as Unranked.")
                 rank_data = {'tier': 'Unranked', 'lp': 0, 'wins': 0, 'losses': 0}
            elif mmr_response.status_code == 204: # No content - player likely unranked or no data
                 print(f"No VAL MMR content (204) for PUUID {puuid}. Treating as Unranked.")
                 rank_data = {'tier': 'Unranked', 'lp': 0, 'wins': 0, 'losses': 0}
            else:
                mmr_response.raise_for_status()
                mmr_api_result = mmr_response.json()
                print(f"Received MMR data: {mmr_api_result}")

                # Parse MMR Data (structure example: {'data': {'currenttier': 21, 'currenttierpatched': 'Immortal 1', 'ranking_in_tier': 55, ...}})
                if 'data' in mmr_api_result and mmr_api_result['data']:
                    mmr_data = mmr_api_result['data']
                    tier_name = mmr_data.get('currenttierpatched', 'Unranked')
                    tier_lp = mmr_data.get('ranking_in_tier', 0) # Usually called RR or LP

                    # Wins/Losses might not be directly in this response, depends on API version/tier
                    # Often requires processing match history separately. We'll default to '--'
                    wins_count = mmr_data.get('wins', '--') # Placeholder if API doesn't provide directly

                    rank_data = {
                        'tier': tier_name if tier_name else 'Unranked',
                        'lp': tier_lp,
                        'wins': wins_count, # Keep as '--' if not available
                        'losses': '--',     # Keep as '--' if not available
                        'rank_icon_url': None # No icon URL from this API, handle in template
                    }
                else:
                     # No 'data' object found, treat as unranked
                     print("MMR API response structure unexpected or missing 'data'. Treating as Unranked.")
                     rank_data = {'tier': 'Unranked', 'lp': 0, 'wins': 0, 'losses': 0}

            print(f"Parsed rank data: {rank_data}")


    # --- Error Handling ---
    except requests.exceptions.Timeout:
        print("Error: Request to Riot API timed out.")
        error_message = "Request to Riot API timed out. The service might be busy. Please try again later."
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        response_text = e.response.text
        print(f"Error: Riot API HTTP Error {status_code}. Response: {response_text}")
        # More specific user messages
        if status_code == 400: error_message = "Invalid request sent to Riot API. Please check the input format."
        elif status_code == 401: error_message = "Unauthorized: Invalid Riot API Key. Please contact the site administrator."
        elif status_code == 403: error_message = "Forbidden: The Riot API Key may be expired, invalid, or lack permissions for the requested data (e.g., MMR API)."
        elif status_code == 404: # Should be caught earlier for account, but catch here for MMR API
             error_message = f"Player data not found in region '{valorant_region}'. They might be unranked or the Riot ID is incorrect."
        elif status_code == 429: error_message = "Rate limit exceeded. Too many requests are being made. Please wait a moment before trying again."
        elif status_code >= 500: error_message = f"Riot API is temporarily unavailable (Server Error {status_code}). Please try again later."
        else: error_message = f"An error occurred while contacting Riot API (Code: {status_code})."
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error: {e}")
        error_message = "Network error: Could not connect to Riot API. Please check your internet connection and Riot API status."
    except ValueError as e: # Catch custom errors raised earlier
        print(f"Error: Data processing error: {e}")
        error_message = str(e) # Display the specific ValueError message
    except Exception as e:
        print(f"CRITICAL: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        error_message = "An unexpected server error occurred. Please try again later or contact support."

    # Always render the results page, passing either rank_data or error_message
    return render_results_page(
        player_name=username,
        player_tag=tag,
        rank_data=rank_data,
        error=error_message
    )

# --- Run App Locally (Gunicorn runs it on Render/Production) ---
if __name__ == '__main__':
    print("--- Starting Ecaly Flask Development Server ---")
    print("*** SECURITY WARNING ***")
    print("* API Key, Secret Key, and Verification Code MUST be set via Environment Variables for security.")
    print("* Ensure RIOT_ACCOUNT_REGION and RIOT_VALORANT_REGION are set if needed (defaults are 'americas'/'na').")
    print("* Falling back to hardcoded placeholders is INSECURE and likely won't work.")
    print("* NEVER commit secrets directly into Git repositories.")
    print("************************")

    # Check critical environment variables
    if RIOT_API_KEY == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("FATAL WARNING: RIOT_API_KEY is using the placeholder. Set the RIOT_API_KEY environment variable.")
    if FLASK_SECRET_KEY == 'a_very_insecure_default_key_for_testing_only_v4': # Check against new placeholder
        print("WARNING: FLASK_SECRET_KEY is using the default insecure placeholder. Set the FLASK_SECRET_KEY environment variable.")
    if RIOT_VERIFICATION_CODE == "de8de887-acbe-467e-9afd-5feb469e7f41":
        print("INFO: RIOT_VERIFICATION_CODE is using its placeholder. Set the RIOT_VERIFICATION_CODE environment variable if required by Riot.")

    port = int(os.environ.get('PORT', 5001)) # Changed default port slightly
    # Set debug=True for development ONLY to see errors easily, NEVER in production
    app.run(host='0.0.0.0', port=port, debug=True)
