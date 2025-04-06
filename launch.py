import os
import streamlit.web.cli as stcli
import sys

# Heroku stellt den Port über die Umgebungsvariable $PORT bereit
os.environ['STREAMLIT_SERVER_PORT'] = os.environ.get('PORT', '8501')
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

# Optional: keine Telemetrie
os.environ["STREAMLIT_BROWSER_GATHERUSAGESTATS"] = "false"

# Starte Streamlit wie gewohnt
sys.argv = ["streamlit", "run", "app.py"]
sys.exit(stcli.main())
