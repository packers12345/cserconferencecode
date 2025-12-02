import os
import sys
import json
import re
from flask import Flask, render_template, request, jsonify, session

# Ensure the project root is on sys.path for package discovery.
# This makes package-style imports work when running this file directly,
# e.g. `python src/app.py` or when invoked from other working directories.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use absolute imports relative to the Systems_Engineering_Chatbot package
from Systems_Engineering_Chatbot.src.env_utils import safe_load_dotenv
from Systems_Engineering_Chatbot.src.context_manager import Conversation
from Systems_Engineering_Chatbot.src.synthesis_engine import SynthesisEngine
from Systems_Engineering_Chatbot.src.api_integration import generate_morphism_proof, generate_isomorphism_justification, generate_l1_mapping, GeminiClient, generate_graph_from_text
from Systems_Engineering_Chatbot.src.morphism_proof_data import MORPHISM_PROOF_DATA
from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
    generate_any_followup_response,
    detect_morphism_graph_trigger,  # ADDED
    generate_hardcoded_morphism_graph_response, # ADDED
)
from Systems_Engineering_Chatbot.src.system_component_extractor import ExtractedSystemSpec
from Systems_Engineering_Chatbot.src.morphism_cache import MorphismCache

# Load environment variables safely
safe_load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Helper functions for prompt parsing
def _extract_system_topic(prompt: str) -> tuple[str | None, str | None]:
    """Extracts the system topic from a prompt."""
    topic_match = re.search(r'for\s(.*?)(?:\.|$)', prompt, re.IGNORECASE)
    if topic_match:
        return topic_match.group(1).strip(), None
    return None, "Please start by defining the system you want to work on. Example: 'Create system requirements for a GPS satellite'."

def _extract_two_systems(prompt: str, error_message: str) -> tuple[str | None, str | None, str | None]:
    """Extracts two system descriptions from a prompt."""
    match = re.search(r'for\s+(?:a\s+|an\s+|the\s+)?(?:system\s+)?(.*?)\s+and\s+(?:a\s+|an\s+|the\s+)?(?:system\s+)?(.*?)(?:\.|$)', prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip(), None
    return None, None, error_message

def _extract_justification_systems(prompt: str) -> tuple[str | None, str | None, str | None]:
    """Extracts system Y and system X for isomorphism justification."""
    match = re.search(r'justify why\s+(.*?)\s+(?:rather than|can be used in(?: in)? replace of|can replace|instead of|versus|and|for|to)\s+(.*?)(?:\.|$)', prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip(), None
    return None, None, "Could not identify the two systems for justification. Please use one of the following formats: 'justify why [System Y] can be used in replace of [System X]', 'justify why one could leverage [System Y] rather than [System X]', or 'justify why [System Y] can replace [System X]'."

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-strong-dev-secret-key")
pdf_path = os.path.join(os.path.dirname(__file__), '..', 'Wach_PF_D_2023 (1).pdf')

# Initialize a single GeminiClient instance
gemini_client_instance = GeminiClient()
synthesis_engine = SynthesisEngine(pdf_path, gemini_client_instance)

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

    # ============================================================================
    # FOLLOW-UP QUERY ROUTING — Check if this is a follow-up to a hard rule response
    # ============================================================================
    # If conversation exists and has a previous hard rule response, route follow-up to LLM
    # Only treat this as a follow-up when the current prompt does NOT itself trigger a hard rule.
    # This ensures explicit Rule 1/Rule 2 prompts are handled as new hard-rule requests.
    if (
        conversation
        and conversation.last_hard_rule_response
        and conversation.last_rule_triggered
        and not (detect_rule_1_trigger(prompt) or detect_rule_2_trigger(prompt) or detect_morphism_graph_trigger(prompt)) # MODIFIED
    ):
        followup_response = generate_any_followup_response(prompt, conversation, gemini_client_instance)
        # Always return the follow-up response (allow the LLM to decide relevance/format)
        session['conversation'] = conversation.to_dict()
        session.modified = True
        return jsonify({
            "response_text": followup_response,
            "system_topic": conversation.system_topic,
            "graph_data": None
        })
    # ============================================================================

    # ============================================================================
    # HARD-OVERRIDE RULES — These rules take absolute precedence over all other logic
    # ============================================================================
    # RULE 1: Mechanical Spring System Design Requests → Return System Z_A exactly
    if detect_rule_1_trigger(prompt):
        # Create or update conversation for Rule 1
        if not conversation:
            conversation = Conversation(system_topic="Mechanical Spring System")
        
        # Generate and store the Rule 1 response
        rule_1_response = generate_rule_1_response()
        conversation.last_rule_triggered = "rule_1"
        conversation.last_hard_rule_response = rule_1_response
        session['conversation'] = conversation.to_dict()
        session.modified = True
        
        # Return System Z_A without any LLM call or PSF/SR logic
        return jsonify({
            "response_text": rule_1_response,
            "system_topic": "Mechanical Spring System (System Z_A)",
            "graph_data": None
        })
    
    # RULE 2: RLC ↔ Mechanical Verification Requests → Return full 2nd-order morphism proof
    if detect_rule_2_trigger(prompt):
        # Create or update conversation for Rule 2
        if not conversation:
            conversation = Conversation(system_topic="RLC Circuit and Mechanical Spring System")
        
        # Generate and store the Rule 2 response
        rule_2_response = generate_rule_2_response()
        conversation.last_rule_triggered = "rule_2"
        conversation.last_hard_rule_response = rule_2_response
        session['conversation'] = conversation.to_dict()
        session.modified = True
        
        # Return complete morphism proof without any LLM call or PSF/SR logic
        return jsonify({
            "response_text": rule_2_response,
            "system_topic": "RLC Circuit and Mechanical Spring System Morphism Verification",
            "graph_data": None
        })
    # ============================================================================

    try:
        # If no conversation exists, the first prompt MUST define the system topic.
        if not conversation:
            topic, error = _extract_system_topic(prompt)
            if error:
                return jsonify({"error": error}), 400
            
            conversation = Conversation(system_topic=topic)
            session['conversation'] = conversation.to_dict() # Save to session immediately
            session.modified = True

        # Visualization request
        if any(keyword in prompt.lower() for keyword in ["visualize", "graph", "diagram", "visualization"]):
            # Ensure system topic is set for visualization
            if not conversation.system_topic:
                topic, error = _extract_system_topic(prompt)
                if error:
                    return jsonify({"error": error}), 400
                conversation.system_topic = topic
                session['conversation'] = conversation.to_dict()
                session.modified = True
            
            # Generate the full graph using the unified API integration function
            graph_data = generate_graph_from_text(conversation, gemini_client_instance)
            
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

        # Homomorphic Proof for Equivalence request
        elif "create a homomorphic proof for this equivalence" in prompt.lower():
            system_x_desc, system_y_desc, error = _extract_two_systems(prompt, "Could not identify the two systems for homomorphic proof. Please use the format: 'create a homomorphic proof for this equivalence for [System X] and [System Y]'.")
            if error:
                return jsonify({"error": error}), 400
            
            try:
                proof_text = generate_morphism_proof(conversation, system_y_desc, gemini_client_instance) # Using generate_morphism_proof
                return jsonify({
                    "response_text": proof_text,
                    "system_topic": conversation.system_topic,
                    "graph_data": None
                })
            except Exception as e:
                print(f"ERROR in homomorphic_proof endpoint: {e}")
                return jsonify({"error": f"An internal server error occurred during homomorphic proof generation: {str(e)}"}), 500

        # L1 Morphism Proof for RLC and Spring System
        elif any(phrase in prompt.lower() for phrase in [
            "assess whether an rlc circuit can be leveraged for a verification model for a mechanical spring system",
            "can an rlc model a spring system",
            "use rlc to verify spring dynamics",
            "are these systems equivalent",
            "mapping between spring and rlc",
            "rlc circuit verification model spring",
            "spring-mass-damper and rlc",
            "rlc and spring equivalence",
            "rlc circuit equivalent to spring",
            "spring damper rlc",
            "rlc circuit morphism spring",
            "prove rlc spring isomorphism",
            "verify rlc spring equivalence",
            "mass spring damper rlc circuit"
        ]):
            return jsonify({
                "response_text": MORPHISM_PROOF_DATA["l1_morphism_proof"],
                "system_topic": conversation.system_topic if conversation else "RLC Circuit and Mechanical Spring System",
                "graph_data": None
            })

        # Isomorphism Justification request
        elif "justify why" in prompt.lower():
            system_y_desc, system_x_desc, error = _extract_justification_systems(prompt)
            if error:
                return jsonify({"error": error}), 400
            
            try:
                justification_text = generate_isomorphism_justification(system_x_desc, system_y_desc, gemini_client_instance)
                return jsonify({
                    "response_text": justification_text,
                    "system_topic": conversation.system_topic,
                    "graph_data": None
                })
            except Exception as e:
                print(f"ERROR in isomorphism justification endpoint: {e}")
                return jsonify({"error": f"An internal server error occurred during justification generation: {str(e)}"}), 500

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
    system_a_desc, system_b_desc, error = _extract_two_systems(prompt, "Could not identify the two systems. Please use the format: '...for [system A] and [system B]' or '...for [system A] to [system B]'.")
    if error:
        return jsonify({"error": error}), 400
    
    # If no conversation exists, create one using the first system as the topic
    if not conversation:
        conversation = Conversation(system_topic=system_a_desc)
        session['conversation'] = conversation.to_dict()
        session.modified = True
    
    try:
        # Call the generation function with the two system descriptions
        proof_data = generate_morphism_proof(conversation, system_b_desc, gemini_client_instance)
        
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

@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    """Clears the entire morphism and system specification cache."""
    cache = MorphismCache()
    cache.clear_all()
    cache.close()
    return jsonify({"message": "Morphism cache cleared successfully."})


@app.route("/l1_mapping", methods=["POST"])
def l1_mapping():
    """Generates an L1 mapping between two abstract system models and returns both a
    human-readable summary and the structured JSON mapping.
    Expected prompt formats (examples):
      - "create an L1 mapping for a mechanical spring and an electric circuit model"
      - "create an l1 mapping for [System A] and [System B]"
    """
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    # Try to extract the two system descriptions from the prompt
    system_a, system_b, error = _extract_two_systems(prompt, "Could not identify the two systems. Please use the format: 'create an L1 mapping for [System A] and [System B]'.")
    if error:
        # Fallback: if the prompt contains the words 'mechanical' and 'electric', map them directly
        if 'mechanical' in prompt.lower() and ('electric' in prompt.lower() or 'electrical' in prompt.lower()):
            system_a = 'mechanical spring-mass-damper'
            system_b = 'series RLC circuit'
        else:
            return jsonify({"error": error}), 400

    try:
        response_text = generate_l1_mapping(system_a, system_b, gemini_client_instance)

        # Save mapping as an artifact in the conversation if available
        conversation_data = session.get('conversation')
        conversation = Conversation.from_dict(conversation_data) if conversation_data else None
        if conversation and not response_text.startswith("### Error"):
            conversation.add_artifact('L1_MAPPING', response_text)
            session['conversation'] = conversation.to_dict()
            session.modified = True

        return jsonify({
            "response_text": response_text,
            "system_topic": conversation.system_topic if conversation else system_a,
            "l1_mapping": None # No longer returning a structured JSON object here
        })
    except Exception as e:
        print(f"ERROR in l1_mapping endpoint: {e}")
        return jsonify({"error": f"An internal server error occurred during L1 mapping generation: {str(e)}"}), 500

@app.route("/isomorphism_visualization", methods=["POST"])
def isomorphism_visualization():
    """Generates a visual graph showing isomorphisms between two systems."""
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        import time
        from Systems_Engineering_Chatbot.src.system_component_extractor import SystemComponentExtractor
        from Systems_Engineering_Chatbot.src.morphism_detector import MorphismDetector, Morphism
        from Systems_Engineering_Chatbot.src.isomorphism_graph_renderer import IsomorphismGraphRenderer
        from Systems_Engineering_Chatbot.src.morphism_justification import JustificationGenerator
        from Systems_Engineering_Chatbot.src.morphism_cache import MorphismCache

        print(f"\n[VISUALIZATION] Starting visualization request: {prompt[:80]}")

        # Extract system names from prompt
        print("[VISUALIZATION] Extracting system names from prompt...")
        # Refined regex to accurately extract system names
        match = re.search(r'(?:mechanical\s+spring\s+system|electric\s+circuit\s+model|rlc\s+circuit|mass-spring-damper\s+system)\s*(?:and|across|vs\.?)\s*(?:mechanical\s+spring\s+system|electric\s+circuit\s+model|rlc\s+circuit|mass-spring-damper\s+system)', prompt, re.IGNORECASE)
        
        if match:
            # Further parse the matched string to get clean system names
            matched_string = match.group(0)
            system_names_found = re.findall(r'(mechanical\s+spring\s+system|electric\s+circuit\s+model|rlc\s+circuit|mass-spring-damper\s+system)', matched_string, re.IGNORECASE)
            
            if len(system_names_found) >= 2:
                system1_name = system_names_found[0].strip()
                system2_name = system_names_found[1].strip()
            else:
                return jsonify({"error": "Could not identify two distinct systems from the prompt."}), 400
        else:
            # Fallback to broader regex if specific keywords not found (though the prompt given has them)
            systems = re.findall(r'(?:for|between|across)\s+(?:a\s+|an\s+|the\s+)?([^,]+?)\s+(?:and|,)\s+(?:a\s+|an\s+|the\s+)?([^.]+?)(?:\.|$)', prompt, re.IGNORECASE)
            if not systems or len(systems[0]) < 2:
                return jsonify({"error": "Could not identify two systems. Use format: 'create a visual for [System 1] and [System 2]'"}), 400
            system1_name = systems[0][0].strip()
            system2_name = systems[0][1].strip()
        
        print(f"[VISUALIZATION] Systems identified: {system1_name} <-> {system2_name}")

        # Initialize components
        extractor = SystemComponentExtractor(gemini_client_instance)
        detector = MorphismDetector(gemini_client_instance)
        renderer = IsomorphismGraphRenderer()
        justifier = JustificationGenerator(gemini_client_instance)
        cache = MorphismCache()

        # Try to use cache first
        print("[VISUALIZATION] Checking cache...")
        cached_morphisms_data = cache.get_cached_morphisms(system1_name, system2_name)
        
        if cached_morphisms_data:
            print("[VISUALIZATION] Using cached data")
            cached_system1_data = cache.get_cached_system(system1_name)
            cached_system2_data = cache.get_cached_system(system2_name)
            
            # Wrap cached dicts in ExtractedSystemSpec
            system1_spec = ExtractedSystemSpec(cached_system1_data)
            system2_spec = ExtractedSystemSpec(cached_system2_data)

            # Convert cached morphism dicts to Morphism objects
            morphisms = [Morphism(**m) for m in cached_morphisms_data]
        else:
            print("[VISUALIZATION] Cache miss - extracting system specifications...")
            
            expert_documentation = ""
            if any(s.lower() in system1_name.lower() for s in ["mechanical spring", "rlc circuit", "electric circuit"]):
                expert_documentation = MORPHISM_PROOF_DATA["l1_morphism_proof"]
            
            start = time.time()
            system1_spec = extractor.extract_system_specification(system1_name, expert_documentation=expert_documentation)
            print(f"[VISUALIZATION] System 1 extracted in {time.time()-start:.2f}s")
            
            expert_documentation = "" # Reset for system2
            if any(s.lower() in system2_name.lower() for s in ["mechanical spring", "rlc circuit", "electric circuit"]):
                expert_documentation = MORPHISM_PROOF_DATA["l1_morphism_proof"]

            start = time.time()
            system2_spec = extractor.extract_system_specification(system2_name, expert_documentation=expert_documentation)
            print(f"[VISUALIZATION] System 2 extracted in {time.time()-start:.2f}s")

            # Cache specifications
            cache.cache_system(system1_name, system1_spec.to_dict())
            cache.cache_system(system2_name, system2_spec.to_dict())

            # Detect morphisms
            print("[VISUALIZATION] Detecting morphisms...")
            start = time.time()
            morphisms = detector.detect_morphisms(system1_spec, system2_spec) # This already returns List[Morphism]
            print(f"[VISUALIZATION] Morphisms detected in {time.time()-start:.2f}s ({len(morphisms)} morphisms)")
            
            # Cache morphisms as a list of dictionaries
            cache.cache_morphisms(system1_name, system2_name, [m.to_dict() for m in morphisms])

        # At this point, 'morphisms' is guaranteed to be List[Morphism]
        morphisms_for_json_response = [m.to_dict() for m in morphisms] # For JSON response

        print("[VISUALIZATION] Rendering visualization...")
        start = time.time()
        visualization_svg = renderer.render_full_visualization(system1_spec, system2_spec, morphisms)
        print(f"[VISUALIZATION] Visualization rendered in {time.time()-start:.2f}s ({len(visualization_svg)} chars)")

        # Generate justification
        print("[VISUALIZATION] Generating justification...")
        start = time.time()
        justification_text = justifier.generate_full_justification(system1_spec, system2_spec, morphisms)
        print(f"[VISUALIZATION] Justification generated in {time.time()-start:.2f}s")

        # Calculate statistics
        iso_count = sum(1 for m in morphisms if m.morphism_type == "ISOMORPHIC")
        homo_count = sum(1 for m in morphisms if m.morphism_type == "HOMOMORPHIC")
        
        def _to_float(value):
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    return 0.5
            return float(value) if value is not None else 0.5
        
        avg_strength = sum(_to_float(m.strength) for m in morphisms) / len(morphisms) if morphisms else 0

        cache.close()

        print(f"[VISUALIZATION] Preparing response: {iso_count} ISO, {homo_count} HOMO, avg={avg_strength:.2%}")
        print("[VISUALIZATION] Request completed successfully!")

        return jsonify({
            "response_text": justification_text,
            "visualization_svg": visualization_svg,
            "morphisms": morphisms_for_json_response, # Use the list of dicts for JSON response
            "statistics": {
                "total_morphisms": len(morphisms),
                "isomorphic_count": iso_count,
                "homomorphic_count": homo_count,
                "average_strength": avg_strength
            },
            "system1_name": system1_name,
            "system2_name": system2_name,
            "system_topic": f"{system1_name} <-> {system2_name}",
            "graph_data": None
        })

    except Exception as e:
        print(f"ERROR in isomorphism_visualization endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during visualization generation: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
