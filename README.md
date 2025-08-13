# Systems_Engineering_Chatbot

## Overview
The Systems Engineering Chatbot is a Flask-based web application designed to assist users in generating system designs, verification requirements, and visualizations based on user inputs. It integrates with external APIs to provide intelligent responses and utilizes user authentication for secure access.

## Dependencies
You will have to get a Gemini API key and neo4j database specifications. You can get a Gemini API key here. https://ai.google.dev/gemini-api/docs/api-key. I will email you the specifications for the database. When you have copied the repository to your local machine, you can enter in your Gemini API Key and neo4j specifications into the fields in the .env. 

## Project Structure
```
Systems_Engineering_Chatbot
├── src
│   ├── app.py                # Main application file
│   ├── api_integration.py     # API integration functions
│   └── templates
│       ├── index.html        # Main index page template
│       └── login.html        # Login page template
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # Project documentation
```

## Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd Systems_Engineering_Chatbot
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory 


4. **Run the Application**
   ```
   python src/app.py
   ```
   Access the application at `http://localhost:5000`.

## Usage
- Navigate to the login page to authenticate.
- After logging in, you can access the main index page where you can input prompts for system design and verification requirements.
- The application will generate responses based on the provided inputs and display visualizations.
- Let me know if things are not working and if particular instructions are unclear. 

