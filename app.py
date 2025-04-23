# Filename: app.py
# --- Imports ---
import requests
from flask import (
    Flask, request, abort, flash, redirect, get_flashed_messages, Response
)
import html  # For escaping user input in HTML
import os # For PORT binding

# --- Configuration & Hardcoded Values ---
# !!! WARNING: Hardcoding secrets like API keys is insecure and not recommended for production! !!!
# !!! This is only for temporary local testing as requested. Use environment variables for deployment. !!!

# Replace with your actual Riot API Key for testing
# !!! DO NOT COMMIT YOUR REAL KEY TO GIT !!!
RIOT_API_KEY = "RGAPI-Your-Actual-Riot-Api-Key-Here" # <<<--- REPLACE ME

# Replace with your actual Riot verification code (from the initial request/image)
RIOT_VERIFICATION_CODE = "de8de887-acbe-467e-9afd-5feb469e7f41" # <<<--- REPLACE ME (if needed)

# Flask secret key (change for better security, even in testing)
# !!! Hardcoding this is also insecure. !!!
FLASK_SECRET_KEY = 'a_very_insecure_default_key_for_testing_only_v3' # <<<--- CHANGE ME

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY # Set the secret key for flashing

# --- Embedded CSS (Enhanced Dark Theme Design) ---
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
    filter: invert(0.8) grayscale(100%) brightness(150%); /* Adjust visibility */
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
    messages = get_flashed_messages(with_categories=true)
    if messages:
        # Wrap messages in container and row/col for proper alignment
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
        {flashed_messages_html} {/* Display flash messages here */}
        <div class="container"> {/* Wrap main content */}
            {content}
        </div>
    </main>
    <footer>
        <p>&copy; {2025} Ecaly - Rank data provided by Riot Games API.</p>
        <p class="small">This is a test application. Use responsibly.</p>
        {/* Verification route /riot.txt is active but intentionally not linked */}
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
    elif rank_data:
        # --- Enhanced Rank Display ---
        tier = html.escape(rank_data.get('tier', 'Unranked'))
        division = html.escape(rank_data.get('division', '')) # Often empty, handle display
        lp = html.escape(str(rank_data.get('lp', '--'))) # Use '--' for missing data
        wins = html.escape(str(rank_data.get('wins', '--')))
        losses = html.escape(str(rank_data.get('losses', '--')))
        icon_url = rank_data.get('rank_icon_url')

        results_content += '<div class="rank-display">' # Flex container

        # Icon
        results_content += '<div class="rank-icon">'
        if icon_url and isinstance(icon_url, str) and icon_url.startswith(('http://', 'https://')):
             results_content += f'<img src="{html.escape(icon_url)}" alt="{tier} Icon">'
        else:
             results_content += '<div style="display:flex; align-items:center; justify-content:center; color: var(--text-muted); font-size: 0.8em;">No Icon</div>'
        results_content += '</div>'

        # Tier & LP
        results_content += '<div class="rank-details text-center">'
        tier_display = f"{tier} {division}".strip() # Combine tier and division, remove trailing space if division is empty
        results_content += f'<h3 class="rank-tier">{tier_display}</h3>'
        results_content += f'<p><strong>LP:</strong> {lp}</p>'
        results_content += '</div>'

        # Stats Row
        results_content += '<div class="stats-row">'
        results_content += f'<div>Wins: <strong>{wins}</strong></div>'
        results_content += f'<div>Losses: <strong>{losses}</strong></div>'
        results_content += '</div>'

        results_content += '</div>' # End rank-display
        # -----------------------------

    else: # Case where rank_data is empty dict {} (e.g., unranked player found)
        results_content += '<div class="alert alert-info" role="alert">Player found, but no specific rank data is available (likely unranked in competitive modes).</div>'

    # Add "Lookup Another" button below results/error/info
    results_content += '<div class="text-center mt-5"><a href="/" class="btn btn-secondary">LOOKUP ANOTHER</a></div>'
    results_content += '</div></div></div>' # End card, col, row

    return render_base_html(title=f"Rank Results - Ecaly", content=results_content)


# --- Flask Routes ---

# <<< --- THIS IS THE /riot.txt ROUTE --- >>>
@app.route('/riot.txt')
def serve_riot_txt():
    """Serves the hardcoded verification code directly."""
    if not RIOT_VERIFICATION_CODE:
        print("CRITICAL: RIOT_VERIFICATION_CODE is not set in the script!")
        # Use abort for server errors
        abort(500, description="Verification code not configured on the server.")
    # Return the code as plain text using Flask Response
    return Response(RIOT_VERIFICATION_CODE, mimetype='text/plain')
# <<< --- END OF /riot.txt ROUTE --- >>>


@app.route('/')
def index():
    """Renders the homepage."""
    return render_index_page()


@app.route('/lookup', methods=['POST'])
def lookup():
    """Handles form submission, calls API, returns results HTML."""
    username = request.form.get('username', '').strip()
    tag = request.form.get('tag', '').strip()

    # Simple validation
    if not username or not tag:
        flash('Please provide both Riot Username and Tagline.', 'warning')
        return redirect('/') # Redirect back to the index page

    # Check if the hardcoded API key looks like the placeholder
    if not RIOT_API_KEY or RIOT_API_KEY == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("ERROR: RIOT_API_KEY is not set or is using the placeholder value in app.py.")
        # Display error on the results page instead of flashing sensitive info
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
        headers = {"X-Riot-Token": RIOT_API_KEY}
        # STEP 1: Get PUUID (Ensure you use the correct region for the account API)
        account_api_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
        account_response = requests.get(account_api_url, headers=headers, timeout=10) # 10 second timeout
        account_response.raise_for_status() # Check for 4xx/5xx errors
        account_data = account_response.json()
        puuid = account_data.get('puuid')

        if not puuid:
            raise ValueError("Could not find PUUID for the given Riot ID. Check username/tag.")
        print(f"Found PUUID: {puuid}")

        # STEP 2: Get Rank Info (Ensure you use the correct region for the VALORANT API)
        # Common regions: na, eu, ap, kr, latam, br
        valorant_region = "na" # <<<--- ADJUST THIS VALORANT REGION AS NEEDED
        rank_api_url = f"https://{valorant_region}.api.riotgames.com/val/ranked/v1/by-puuid/{puuid}"
        rank_response = requests.get(rank_api_url, headers=headers, timeout=10) # 10 second timeout

        if rank_response.status_code == 404:
            # Player found via account API, but no VAL rank data (common for unranked/new players)
            print(f"No VAL ranked data found for PUUID {puuid} (status 404).")
            rank_data = {} # Represent as 'found but unranked'
        elif rank_response.status_code == 200:
            api_result = rank_response.json()
            print(f"Received rank data: {api_result}") # Log raw data for debugging

            # --- !!! IMPORTANT: PARSE RESPONSE CAREFULLY (CHECK RIOT DOCS) !!! ---
            # This parsing is HIGHLY DEPENDENT on the exact structure returned by Riot, which can change.
            # You MUST inspect the actual `api_result` JSON to get the correct keys.
            # Example parsing (likely needs adjustment):
            # Find the most relevant competitive update if available
            comp_updates = api_result.get('QueueData', {}).get('competitive',{}).get('Matches',[])
            latest_update = comp_updates[0] if comp_updates else {}

            rank_data = {
                 'tier': latest_update.get('TierName', 'Unranked'),  # Example key
                 'division': '', # Often part of tier name, or maybe 'TierDivision'
                 'lp': latest_update.get('TierProgress', 'N/A'), # Example key
                 'wins': api_result.get('Wins', 'N/A'), # Example key (may be overall wins)
                 'losses': api_result.get('Losses', 'N/A'), # Example key
                 'rank_icon_url': latest_update.get('TierIcon', None) # Example key
            }
            # ---------------------------------------------------------------------
            print(f"Parsed rank data: {rank_data}")
        else:
            # Handle other non-404 errors from the rank API
            rank_response.raise_for_status()

    # --- Error Handling ---
    except requests.exceptions.Timeout:
        print("Error: Request to Riot API timed out.")
        error_message = "Request to Riot API timed out. The API might be slow or unreachable."
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print(f"Error: Riot API HTTP Error {status_code}")
        # Provide more user-friendly messages for common errors
        if status_code == 400: error_message = "Invalid request sent to Riot API (check username/tag format?)."
        elif status_code == 403: error_message = "Forbidden - Check the Riot API Key permissions or validity."
        elif status_code == 404: error_message = "Player not found with that Riot ID (check username/tag and account region)."
        elif status_code == 429: error_message = "Rate limit exceeded - Please wait a moment before trying again."
        elif status_code >= 500: error_message = "Riot API is temporarily unavailable (Server Error)."
        else: error_message = f"Riot API Error (Code: {status_code}). Please try again later."
    except requests.exceptions.RequestException as e:
        # Catch potential network errors (DNS, connection refused, etc.)
        print(f"Error: Network error connecting to Riot API: {e}")
        error_message = "Network error - Could not connect to Riot API. Check internet connection."
    except ValueError as e:
         # Catch specific errors raised in the try block (like PUUID not found)
         print(f"Error: Data processing error: {e}")
         error_message = str(e)
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"CRITICAL: An unexpected error occurred: {e}") # Log the full error
        error_message = "An unexpected server error occurred during lookup." # Generic message to user

    # --- Render results page HTML string ---
    return render_results_page(
        player_name=username,
        player_tag=tag,
        rank_data=rank_data, # Will be None on error, {} if unranked, or dict if ranked
        error=error_message # Will be None if successful
    )


# --- Run App Locally (Gunicorn runs it on Render/Production) ---
if __name__ == '__main__':
    print("--- Starting Ecaly Flask Development Server ---")
    print("*** SECURITY WARNING ***")
    print("* API Key and Secret Key may be hardcoded in this script for testing.")
    print("* NEVER commit secrets directly into Git repositories.")
    print("* Use environment variables for production deployments (e.g., on Render).")
    print("************************")
    if RIOT_API_KEY == "RGAPI-Your-Actual-Riot-Api-Key-Here":
        print("WARNING: Placeholder RIOT_API_KEY detected in script.")
    if FLASK_SECRET_KEY == 'a_very_insecure_default_key_for_testing_only_v3':
        print("WARNING: Default insecure FLASK_SECRET_KEY detected.")

    # Use PORT environment variable if available (used by Render/hosting), otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    # debug=False is crucial for Render compatibility and security. Set True ONLY for local debugging.
    app.run(host='0.0.0.0', port=port, debug=False)
