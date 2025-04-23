# Filename: app.py
# --- Imports ---
import requests
from flask import (
    Flask, request, abort, flash, redirect, get_flashed_messages, Response
)
import html  # For escaping user input in HTML
import os  # For PORT binding
import datetime  # To get the current year for the footer

# --- Configuration & Hardcoded Values ---
# !!! WARNING: Use Environment Variables on Render for secrets! Hardcoding is insecure! !!!

# Use Environment Variables first, fall back to placeholders (INSECURE for production)
RIOT_API_KEY = os.environ.get("RIOT_API_KEY", "RGAPI-Your-Actual-Riot-Api-Key-Here")
RIOT_VERIFICATION_CODE = os.environ.get("RIOT_VERIFICATION_CODE", "de8de887-acbe-467e-9afd-5feb469e7f41")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", 'a_very_insecure_default_key_for_testing_only_v3')

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY  # Set the secret key for flashing

# --- Embedded CSS (Enhanced Dark Theme Design) ---
# (CSS remains the same as provided - no changes needed here)
CUSTOM_CSS = """
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Basic Reset & Dark Theme Variables */
:root {
    --bg-color: #121212; /* Very dark background */
    --surface-color: #1e1e1e; /* Card/Surface background */
    --primary-color: #00bcd4; /* Cyan accent */
    --primary-hover: #0097a7;
    --text-color: #e0e0e0; /* Light text */
    --text-muted: #888; /* Muted text */
    --border-color: #333; /* Subtle borders */
    --error-color: #f44336;
    --warning-color: #ff9800;
    --success-color: #4caf50;
    --font-family: 'Poppins', sans-serif;
}

html {
    scroll-behavior: smooth;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: var(--font-family);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    line-height: 1.6;
}

main {
    flex: 1; /* Allows main content to grow and push footer down */
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Navbar Styling */
.navbar {
    background-color: var(--surface-color) !important; /* Override Bootstrap */
    border-bottom: 1px solid var(--border-color);
    padding: 0.8rem 0;
    position: sticky; /* Make navbar sticky */
    top: 0;
    z-index: 1000; /* Ensure it's above other content */
}
.navbar-brand {
    font-weight: 600;
    color: var(--primary-color) !important; /* Accent color for brand */
    font-size: 1.5rem;
}
.navbar-brand:hover {
    color: var(--primary-hover) !important;
}

/* Card Styling (Lookup & Results) */
.styled-card {
    background-color: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 2.5rem; /* More padding */
    margin-top: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); /* Subtle shadow */
}
.styled-card .card-title {
    color: var(--text-color);
    font-weight: 600;
    margin-bottom: 1.5rem;
}

/* Form Styling */
.form-label {
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 0.5rem;
}
.form-control {
    background-color: #2c2c2c; /* Slightly lighter input bg */
    border: 1px solid var(--border-color);
    color: var(--text-color);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.form-control:focus {
    background-color: #333;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(0, 188, 212, 0.25); /* Cyan focus glow */
    color: var(--text-color);
}
.form-control::placeholder {
    color: #666;
}
.input-group-text {
    background-color: #2c2c2c;
    border: 1px solid var(--border-color);
    color: var(--text-muted);
}

/* Button Styling */
.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-weight: 600;
    transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
    cursor: pointer;
    text-transform: uppercase; /* Uppercase button text */
    letter-spacing: 0.5px; /* Slight letter spacing */
}
.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    color: #111; /* Dark text on light button */
}
.btn-primary:hover {
    background-color: var(--primary-hover);
    border-color: var(--primary-hover);
    transform: translateY(-2px); /* Slight lift on hover */
    box-shadow: 0 4px 8px rgba(0, 188, 212, 0.2); /* Add shadow on hover */
    color: #111;
}
.btn-secondary {
    background-color: #444;
    border-color: #444;
    color: var(--text-color);
}
.btn-secondary:hover {
    background-color: #555;
    border-color: #555;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    color: var(--text-color);
}
.d-grid .btn {
    width: 100%;
}

/* Results Card Specific Styling */
.result-card h2 {
    font-weight: 600;
    margin-bottom: 1rem; /* Reduced margin */
}
.result-card .player-id {
    color: var(--text-muted);
    margin-bottom: 2rem;
    font-size: 1.1em;
}
.result-card hr {
    border-color: var(--border-color);
    margin: 1.5rem 0; /* Consistent margin for HR */
}

.rank-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem; /* Reduced gap */
}
.rank-icon img, .rank-icon div { /* Style both image and placeholder div */
    width: 110px; /* Slightly larger icon */
    height: 110px;
    object-fit: contain;
    background-color: rgba(255, 255, 255, 0.03); /* Even more subtle bg */
    border-radius: 50%;
    padding: 10px;
    border: 1px solid var(--border-color);
    margin-bottom: 0.5rem; /* Space below icon */
}
.rank-tier {
    font-size: 2rem; /* Larger tier text */
    font-weight: 700;
    color: var(--primary-color);
    margin: 0;
    text-transform: uppercase;
}
.rank-details p {
    margin-bottom: 0.3rem; /* Tighter spacing */
    color: var(--text-muted);
    font-size: 1.1rem; /* Slightly larger detail text */
}
.rank-details strong {
    color: var(--text-color);
    font-weight: 600;
}
.stats-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem; /* More space between Wins/Losses */
    margin-top: 1.5rem;
    font-size: 1.1rem;
}
.stats-row div { color: var(--text-muted); }
.stats-row strong { color: var(--text-color); }

/* Alert Styling */
.alert {
    border: none;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-top: 1.5rem; /* Ensure space above alerts */
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.95em;
}
.alert strong {
    font-weight: 600;
    margin-right: 0.5em;
}
.alert-danger { background-color: rgba(220, 53, 69, 0.2); color: #f8d7da; border-left: 4px solid #dc3545; }
.alert-warning { background-color: rgba(255, 193, 7, 0.2); color: #fff3cd; border-left: 4px solid #ffc107; }
.alert-success { background-color: rgba(40, 167, 69, 0.2); color: #d4edda; border-left: 4px solid #28a745; }
.alert-info { background-color: rgba(23, 162, 184, 0.2); color: #d1ecf1; border-left: 4px solid #17a2b8; }

.btn-close {
    filter: invert(0.8) grayscale(100%) brightness(150%); /* Adjust RIGHTS visibility */
}

/* Footer Styling */
footer {
    background-color: var(--surface-color);
    border-top: 1px solid var(--border-color);
    padding: 2rem 0; /* More padding */
    color: var(--text-muted);
    font-size: 0.9em;
    margin-top: auto; /* Pushes footer to bottom */
    text-align: center;
}
footer p { margin-bottom: 0.5rem; }
"""

# --- HTML Templates (as Python functions returning strings) ---

def render_base_html(title="Ecaly", content="", head_extra="", scripts_extra=""):
    """Simulates base.html template with enhanced styling."""
    flashed_messages_html = ""
    # Use Python's True
    messages = get_flashed_messages(with_categories=True)
    if messages:
        flashed_messages_html += "<div class='container'><div class='row justify-content-center'><div class='col-lg-8 col-md-10'>"
        for category, message in messages:
            safe_message = html.escape(message)
            alert_class = category if category in ['danger', 'warning', 'success', 'info'] else 'info'
            flashed_messages_html += f'''
            <div class="alert alert-{alert_class} alert-dismissible fade show" role="alert">
                <span>{safe_message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            '''
        flashed_messages_html += "</div></div></div>"

    # Get current year for footer
    current_year = datetime.datetime.now().year

    # Use correct HTML comment syntax
    return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    {head_extra}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap-reboot.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap-grid.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap-utilities.min.css" rel="stylesheet">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>{CUSTOM_CSS}</style>
</head>
<body>
    <nav class="navbar">
        <div class="container"><a class="navbar-brand" href="/">ECALY</a></div>
    </nav>
    <main>
        {flashed_messages_html}
        <div class="container">
            {content}
        </div>
    </main>
    <footer>
        <p>© {current_year} Ecaly - Rank data provided by Riot Games API.</p>
        <p class="small">This is a test application. Use responsibly.</p>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    {scripts_extra}
</body>
</html>
"""

def render_index_page():
    """Renders the content for the index page with new styles."""
    index_content = """
<div class="row justify-content-center">
    <div class="col-lg-6 col-md-8">
        <div class="styled-card"> {/* Use new card class */}
            <h2 class="card-title text-center">Valorant Rank Lookup</h2>
            <p class="text-center text-muted mb-4">Enter a player's Riot ID below.</p>
            <form action="/lookup" method="post">
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" name="username" placeholder="PlayerName" required>
                </div>
                <div class="input-group mb-4"> {/* More space below input group */}
                     <span class="input-group-text">#</span>
                     <input type="text" class="form-control" id="tag" name="tag" placeholder="TAG" required>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-primary btn-lg">LOOKUP RANK</button>
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

    results_content = f"""
<div class="row justify-content-center">
    <div class="col-lg-6 col-md-8">
        <div class="styled-card result-card"> {/* Use new card class */}
            <h2 class="text-center">Rank Result</h2>
            <p class="text-center player-id">{safe_player_name}#{safe_player_tag}</p>
            <hr>
"""
    if safe_error:
        results_content += f'<div class="alert alert-danger" role="alert"><strong>Lookup Failed:</strong> {safe_error}</div>'
    elif rank_data is not None:  # Check if rank_data is not None (covers {} case too)
        # --- Enhanced Rank Display ---
        tier = html.escape(rank_data.get('tier', 'Unranked'))  # Default to Unranked
        division = html.escape(rank_data.get('division', ''))
        lp = html.escape(str(rank_data.get('lp', '--')))
        wins = html.escape(str(rank_data.get('wins', '--')))
        losses = html.escape(str(rank_data.get('losses', '--')))
        icon_url = rank_data.get('rank_icon_url')

        results_content += '<div class="rank-display">'  # Flex container

        # Icon
        results_content += '<div class="rank-icon">'
        if icon_url and isinstance(icon_url, str) and icon_url.startswith(('http://', 'https://')):
             results_content += f'<img src="{html.escape(icon_url)}" alt="{tier} Icon">'
        else:
             # Placeholder if no icon or if rank_data was {} (unranked)
             results_content += '<div style="display:flex; align-items:center; justify-content:center; color: var(--text-muted); font-size: 0.8em;">No Icon</div>'
        results_content += '</div>'

        # Tier & LP
        results_content += '<div class="rank-details text-center">'
        tier_display = f"{tier} {division}".strip()
        results_content += f'<h3 class="rank-tier">{tier_display}</h3>'
        # Only show LP/Wins/Losses if they are meaningful (not '--')
        if lp != '--':
             results_content += f'<p><strong>LP:</strong> {lp}</p>'
        results_content += '</div>'

        # Stats Row (only show if wins/losses are meaningful)
        if wins != '--' or losses != '--':
            results_content += '<div class="stats-row">'
            results_content += f'<div>Wins: <strong>{wins}</strong></div>'
            results_content += f'<div>Losses: <strong>{losses}</strong></div>'
            results_content += '</div>'

        results_content += '</div>'  # End rank-display

        # Add message for unranked case (where rank_data might be {})
        if not rank_data.get('tier') or rank_data.get('tier') == 'Unranked':
             if not safe_error:  # Avoid double messaging if there was also an error somehow
                  results_content += '<div class="alert alert-info mt-4" role="alert">Player found, but appears unranked in competitive modes.</div>'
        # -----------------------------

    # Fallback/Error case already handled by the first 'if safe_error:' check

    # Add "Lookup Another" button below results/error/info
    results_content += '<div class="text-center mt-5"><a href="/" class="btn btn-secondary">LOOKUP ANOTHER</a></div>'
    results_content += '</div></div></div>'  # End card, col, row

    return render_base_html(title=f"Rank Results - Ecaly", content=results_content)

# --- Flask Routes ---

@app.route('/riot.txt')
def serve_riot_txt():
    """Serves the verification code directly."""
    # Use the value fetched from ENV or the hardcoded placeholder
    current_verification_code = RIOT_VERIFICATION_CODE
    if not current_verification_code or current_verification_code == "de8de887-acbe-467e-9afd-5feb469e7f41":
        print("WARNING: RIOT_VERIFICATION_CODE is not set via ENV or is using the placeholder!")
        # Allow serving placeholder for initial setup, but log warning. Consider aborting in production.
        # abort(500, description="Verification code not configured on the server.")

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
        return redirect('/')

    # Check if API key is missing or still the placeholder
    current_api_key = RIOT_API_KEY
    if not current_api_key or current_api_key == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("ERROR: RIOT_API_KEY environment variable not set or is using the placeholder value.")
        flash('Application configuration error: API key missing or invalid. Please contact the administrator.', 'danger')
        return render_results_page(
            player_name=username,
            player_tag=tag,
            error='Application configuration error. API key missing.'
        )

    # --- Riot API Call Logic ---
    rank_data = None
    error_message = None
    print(f"Looking up player: {username}#{tag}")

    try:
        headers = {"X-Riot-Token": current_api_key}
        # Use environment variables for regions, falling back to defaults
        account_region = os.environ.get("RIOT_ACCOUNT_REGION", "americas")
        valorant_region = os.environ.get("RIOT_VALORANT_REGION", "na")

        # STEP 1: Get PUUID
        account_api_url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
        print(f"Calling Account API: {account_api_url}")
        account_response = requests.get(account_api_url, headers=headers, timeout=15)
        account_response.raise_for_status()
        account_data = account_response.json()
        puuid = account_data.get('puuid')

        if not puuid:
            raise ValueError("Could not find PUUID for the given Riot ID. Check username/tag and account region.")
        print(f"Found PUUID: {puuid}")

        # STEP 2: Get Rank Info
        # Verify this endpoint and its response structure against current Riot API docs
        rank_api_url = f"https://{valorant_region}.api.riotgames.com/val/ranked/v1/by-puuid/{puuid}"
        print(f"Calling Rank API: {rank_api_url}")
        rank_response = requests.get(rank_api_url, headers=headers, timeout=15)

        if rank_response.status_code == 404:
            print(f"No VAL ranked data found for PUUID {puuid} (status 404). Assuming unranked.")
            rank_data = {'tier': 'Unranked'}  # Explicitly represent as unranked
        else:
            rank_response.raise_for_status()
            api_result = rank_response.json()
            print(f"Received rank data: {api_result}")  # Log raw response

            # --- !!! ADAPT PARSING BASED ON ACTUAL `api_result` LOGGED ABOVE !!! ---
            competitive_data = None
            # Example parsing attempts - CHECK THE LOGS FOR THE REAL STRUCTURE
            if isinstance(api_result.get('data'), list) and len(api_result['data']) > 0:
                 rank_info = api_result['data'][0]
                 competitive_data = {
                     'tier_name': rank_info.get('rankedRating', 'Unranked'),  # Key might be different
                     'tier_progress': rank_info.get('competitiveTier', 0),  # Key might be different
                     'wins': rank_info.get('numberOfWins', '--'),  # Key might be different
                     'losses': rank_info.get('numberOfLosses', '--'),  # Key might be different
                     'icon': None  # Icon usually needs mapping
                 }
            # Add more 'elif' checks here for other possible structures based on api_result logs

            if not competitive_data:
                 print("Could not find expected competitive data structure in API response.")
                 competitive_data = {}  # Ensure it exists for .get() calls below

            # Default values
            tier_name = "Unranked"
            tier_progress = "--"
            wins_count = "--"
            losses_count = "--"
            tier_icon = None

            # Extract data using .get() with defaults
            # *** ADJUST THESE KEYS based on the actual structure found in `competitive_data` ***
            tier_name = competitive_data.get('tier_name', 'Unranked')
            tier_progress = competitive_data.get('tier_progress', '--')
            wins_count = competitive_data.get('wins', '--')
            losses_count = competitive_data.get('losses', '--')
            tier_icon = competitive_data.get('icon', None)  # Or derive from tier_name/tier_progress

            rank_data = {
                 'tier': tier_name,
                 'division': '',  # Often combined in tier name
                 'lp': tier_progress,
                 'wins': wins_count,
                 'losses': losses_count,
                 'rank_icon_url': tier_icon
            }
            # --- End Parsing Logic ---

            print(f"Parsed rank data: {rank_data}")

    except requests.exceptions.Timeout:
        print("Error: Request to Riot API timed out.")
        error_message = "Request to Riot API timed out. Please try again later."
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        response_text = e.response.text
        print(f"Error: Riot API HTTP Error {status_code}. Response: {response_text}")
        if status_code == 400: error_message = "Invalid request (check username/tag format?)."
        elif status_code == 401: error_message = "Unauthorized - Check the Riot API Key (ensure it's valid and not expired)."
        elif status_code == 403: error_message = "Forbidden - Check the Riot API Key permissions or validity. It might be expired or invalid."
        elif status_code == 404:
             error_message = "Player not found with that Riot ID/Region (check spelling, tag, and regions)."
        elif status_code == 429: error_message = "Rate limit exceeded - Please wait a moment before trying again."
        elif status_code >= 500: error_message = f"Riot API is temporarily unavailable (Server Error {status_code}). Please try again later."
        else: error_message = f"Riot API Error (Code: {status_code}). Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error: {e}")
        error_message = "Network error - Could not connect to Riot API. Check internet connection and API status."
    except ValueError as e:  # Catch PUUID not found error
        print(f"Error: Data processing error: {e}")
        error_message = str(e)
    except Exception as e:
        print(f"CRITICAL: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        error_message = "An unexpected server error occurred during lookup."

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
    print("* API Key, Secret Key, and Verification Code should be set via Environment Variables for security.")
    print("* This script might fall back to hardcoded placeholders if ENV VARS are not set.")
    print("* NEVER commit secrets directly into Git repositories.")
    print("************************")

    # Check placeholders and print warnings
    if RIOT_API_KEY == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("WARNING: RIOT_API_KEY is using the placeholder. Set the RIOT_API_KEY environment variable.")
    if FLASK_SECRET_KEY == 'a_very_insecure_default_key_for_testing_only_v3':
        print("WARNING: FLASK_SECRET_KEY is using the default insecure placeholder. Set the FLASK_SECRET_KEY environment variable.")
    if RIOT_VERIFICATION_CODE == "de8de887-acbe-467e-9afd-5feb469e7f41":
        print("INFO: RIOT_VERIFICATION_CODE is using the placeholder. Set the RIOT_VERIFICATION_CODE environment variable if needed.")

    port = int(os.environ.get('PORT', 5000))
    # Keep debug=False for Render
    app.run(host='0.0.0.0', port=port, debug=False)
