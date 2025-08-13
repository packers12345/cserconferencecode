# Systems Engineering Chatbot

This is a Flask-based chatbot for systems engineering tasks. It uses a combination of a local knowledge base (from a PDF document) and generative AI to solve systems engineering queries, generate systemartifacts, and create visualizations.

## Prerequisites

*   Python 3.x
*   pip (Python package installer)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/packers12345/cserconferencecode.git
    cd cserconferencecode/Systems_Engineering_Chatbot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Environment Variables

Create a `.env` file in the `src` directory (`Systems_Engineering_Chatbot/src/.env`) and add the following environment variables.

```
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=your_neo4j_database
GEMINI_API_KEY=your_gemini_api_key
FLASK_SECRET_KEY=a_strong_secret_key
```

*   **`NEO4J_*`**: Credentials for your Neo4j AuraDB instance. These will be provided upon request.
*   **`GEMINI_API_KEY`**: Your API key for the Google Gemini model. You can obtain one from the [Google AI Studio](https://aistudio.google.com/app/apikey).
*   **`FLASK_SECRET_KEY`**: A secret key for Flask sessions. You can generate one yourself.

## Running the Application

1.  **Ensure the PDF knowledge base is present:**
    The application expects a file named `Wach_PF_D_2023 (1).pdf` to be in the `Systems_Engineering_Chatbot` directory.

2.  **Run the Flask application:**
    From the `Systems_Engineering_Chatbot` directory, run:
    ```bash
    python src/app.py
    ```

3.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:5001`.

## File Structure

```
Systems_Engineering_Chatbot/
├── src/
│   ├── app.py                  # Main Flask application
│   ├── context_manager.py      # Manages conversation context
│   ├── synthesis_engine.py     # Handles response generation
│   ├── api_integration.py      # Integrates with external APIs (Gemini)
│   ├── neo4j_integration.py    # Integrates with Neo4j
│   ├── systems_engineering_graph.py # Generates system graphs
│   ├── templates/
│   │   └── index.html          # Main HTML template
│   └── .env                    # Environment variables (create this file)
├── requirements.txt            # Python dependencies
├── Wach_PF_D_2023 (1).pdf      # Knowledge base document
└── README.md                   # This file
