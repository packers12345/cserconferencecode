import os
import json
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from context_manager import Conversation
from synthesis_engine import SynthesisEngine
from systems_engineering_graph import create_full_system_graph
from api_integration import generate_morphism_proof

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-strong-dev-secret-key")
pdf_path = os.path.join(os.path.dirname(__file__), '..', 'Wach_PF_D_2023 (1).pdf')
synthesis_engine = SynthesisEngine(pdf_path)

@app.route("/")
def index():
    """Renders the main chat interface, displaying the current system topic if available."""
    conversation_data = session.get('conversation')
    topic = conversation_data.get('system_topic', '') if conversation_data else ''
    return render_template("index.html", system_topic=topic)

@app.route("/chat", methods=["POST"])
def chat():
    """Handles the main chat logic using the Conversation class for context management."""
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    # Load conversation from session or create a new one
    conversation_data = session.get('conversation')
    conversation = Conversation.from_dict(conversation_data) if conversation_data else None

    # If the user is defining a new system, always start a new conversation
    if "create system requirements for" in prompt.lower():
        conversation = None

    try:
        # If no conversation exists, the first prompt MUST define the system topic.
        if not conversation:
            # A more robust regex to capture the system topic after "for"
            topic_match = re.search(r'for\s(.*?)(?:\.|$)', prompt, re.IGNORECASE)
            if not topic_match:
                return jsonify({
                    "error": "Please start by defining the system you want to work on. Example: 'Create system requirements for a GPS satellite'."
                }), 400
            
            topic = topic_match.group(1).strip()
            
            conversation = Conversation(system_topic=topic)
            session['conversation'] = conversation.to_dict() # Save to session immediately
            session.modified = True

        # Visualization request
        if any(keyword in prompt.lower() for keyword in ["visualize", "graph", "diagram", "visualization"]):
            # Ensure system topic is set for visualization
            if not conversation.system_topic:
                # Attempt to extract topic from the current prompt
                topic_match = re.search(r'for\s(.*?)(?:\.|$)', prompt, re.IGNORECASE)
                if not topic_match:
                    return jsonify({
                        "error": "Please specify the system topic for visualization. Example: 'Create a graph visualization for a drone delivery system'."
                    }), 400
                conversation.system_topic = topic_match.group(1).strip()
                session['conversation'] = conversation.to_dict()
                session.modified = True
            
            # Generate the full graph using the new generative module
            graph_data = create_full_system_graph(conversation.system_topic)
            
            return jsonify({
                "response_text": f"Here is a generated system visualization for the **{conversation.system_topic}**.",
                "system_topic": conversation.system_topic,
                "graph_data": graph_data
            })

        # Traceability Matrix request
        elif "traceability matrix" in prompt.lower():
            # The new deterministic approach: generate the entire matrix in one go.
            matrix_html = synthesis_engine.generate_traceability_matrix(conversation.system_topic)
            
            return jsonify({
                "response_text": matrix_html,
                "system_topic": conversation.system_topic,
                "graph_data": None
            })

        # Artifact generation request
        else:
            # Determine artifact type from prompt for structured storage
            artifact_type = "Unknown"
            if "system requirements" in prompt.lower(): artifact_type = "SR"
            elif "system design" in prompt.lower(): artifact_type = "SD"
            elif "verification requirement" in prompt.lower(): artifact_type = "VR"
            elif "verification model" in prompt.lower(): artifact_type = "VM"

            new_text = synthesis_engine.generate_response(prompt, conversation.get_context_for_text_generation())
            conversation.add_artifact(artifact_type, new_text)
            session['conversation'] = conversation.to_dict()
            session.modified = True

            return jsonify({
                "response_text": new_text,
                "system_topic": conversation.system_topic,
                "graph_data": None
            })

    except Exception as e:
        print(f"ERROR in chat endpoint: {e}")
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@app.route("/morphism_proof", methods=["POST"])
def morphism_proof():
    """Handles the dynamic generation of a morphism proof, creating a context if one doesn't exist."""
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    conversation_data = session.get('conversation')
    conversation = Conversation.from_dict(conversation_data) if conversation_data else None

    # A more flexible regex to capture the two systems from the prompt.
    # This handles "for [system A] and [system B]" or "for [system A] to [system B]"
    match = re.search(r'for\s+(.*?)\s+(?:and|to)\s+(?:a\s+)?(.*?)(?:\.|$)', prompt, re.IGNORECASE)
    if not match:
        return jsonify({
            "error": "Could not identify the two systems. Please use the format: '...for [system A] and [system B]' or '...for [system A] to [system B]'."
        }), 400
    
    system_a_desc = match.group(1).strip()
    system_b_desc = match.group(2).strip()

    # If no conversation exists, create one using the first system as the topic
    if not conversation:
        conversation = Conversation(system_topic=system_a_desc)
        session['conversation'] = conversation.to_dict()
        session.modified = True
    
    try:
        # Call the generation function with the two system descriptions
        proof_data = generate_morphism_proof(conversation, system_b_desc)
        
        return jsonify({
            "response_text": proof_data,
            "system_topic": conversation.system_topic, # This will be system_a_desc
            "graph_data": None
        })
    except Exception as e:
        print(f"ERROR in morphism_proof endpoint: {e}")
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@app.route("/clear_context", methods=["POST"])
def clear_context():
    """Clears the conversation from the session."""
    session.pop('conversation', None)
    return jsonify({"message": "Context cleared successfully.", "system_topic": ""})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
