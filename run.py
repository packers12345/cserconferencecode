import os
import sys

import os
import sys

# Add the project root directory to sys.path for package discovery
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the Flask app from the Systems_Engineering_Chatbot.src.app module
from Systems_Engineering_Chatbot.src.app import app

if __name__ == "__main__":
    # Run the Flask application
    # The port is configured in app.py, default is 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
