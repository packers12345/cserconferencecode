import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from context_manager import Conversation

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def get_gemini_client():
    """Configures and returns a Gemini client."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file.")
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def load_prompt_from_file(filename: str) -> str:
    """Loads a prompt from a markdown file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def generate_morphism_proof(conversation: Conversation, system_b_description: str) -> str:
    """
    Dynamically generates a morphism proof using a context-rich, single-shot prompt.
    This function now uses a hardcoded deterministic prompt.
    """
    model = get_gemini_client()
    system_a_description = conversation.system_topic

    # Hardcoded, deterministic prompt for generating the homomorphism proof
    final_prompt = f"""
    You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a formal mathematical proof of the existence of a homomorphism between a source system model (`Z_A`) and a target system model (`Z_B`). The proof must be narrative, rigorous, and adapt the structure of the example below to the specific systems provided.

    **User's Prompt:** "Create a homomorphism proof for a {system_a_description} and a {system_b_description}."

    **CRITICAL INSTRUCTIONS:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
    2.  **Define the Systems:** First, create plausible, formal definitions for both `Z_A` ({system_a_description}) and `Z_B` ({system_b_description}). Each system must be defined as a 5-tuple: `(S, X, Y, N, R)`. The states, inputs, and outputs should be relevant to the system's description.
    3.  **Define the Homomorphism:** Clearly define the three mapping functions: `h_S` (State Map), `h_X` (Input Map), and `h_Y` (Output Map). These mappings must be logical and consistent with the system definitions.
    4.  **Verify the Conditions:** Rigorously verify the two core conditions of a homomorphism for at least two representative state-input pairs. If a direct mapping is not possible, explain why and what assumptions are being made.
        *   **Transition Preservation:** `h_S(N_A(s_A, x_A)) = N_B(h_S(s_A), h_X(x_A))`
        *   **Output Preservation:** `h_Y(R_A(s_A, x_A)) = R_B(h_S(s_A), h_X(x_A))`
    5.  **Provide a Conclusion:** State whether the homomorphism is valid based on your verification, and clearly state any assumptions made during the proof.

    ---
    **EXAMPLE OF A RIGOROUS HOMOMORPHISM PROOF (ADAPT THIS STRUCTURE):**

    ### Homomorphism Proof: [System A] to [System B]

    This document provides a formal proof of the existence of a homomorphism `h` from a [System A] `Z_A` to a [System B] `Z_B`.

    **1. System Z_A ([System A])**

    *   **States (S_A):** `{{s_A1: [State 1], s_A2: [State 2], ...}}`
    *   **Inputs (X_A):** `{{x_A1: [Input 1], x_A2: [Input 2], ...}}`
    *   **Outputs (Y_A):** `{{y_A1: [Output 1], y_A2: [Output 2], ...}}`
    *   **Next State Function (N_A):**
        *   `N_A(s_A1, x_A1) = s_A2`
        *   ...
    *   **Readout Function (R_A):**
        *   `R_A(s_A2, x_A2) = y_A1`
        *   ...

    **2. System Z_B ([System B])**

    *   **States (S_B):** `{{s_B1: [State 1], s_B2: [State 2], ...}}`
    *   **Inputs (X_B):** `{{x_B1: [Input 1], x_B2: [Input 2], ...}}`
    *   **Outputs (Y_B):** `{{y_B1: [Output 1], y_B2: [Output 2], ...}}`
    *   **Next State Function (N_B):**
        *   `N_B(s_B1, x_B1) = s_B2`
        *   ...
    *   **Readout Function (R_B):**
        *   `R_B(s_B2, x_B2) = y_B1`
        *   ...

    **3. Define the Homomorphism `h`**

    *   **State Map (h_S):**
        *   `h_S(s_A1) = s_B1`
        *   ...
    *   **Input Map (h_X):**
        *   `h_X(x_A1) = x_B1`
        *   ...
    *   **Output Map (h_Y):**
        *   `h_Y(y_A1) = y_B1`
        *   ...

    **4. Verification of Conditions**

    *   **Case 1: ([State], [Input])**
        *   **Transition Preservation:**
            *   LHS: `h_S(N_A(...)) = ...`
            *   RHS: `N_B(h_S(...), h_X(...)) = ...`
            *   LHS = RHS. The condition holds.
        *   **Output Preservation:**
            *   LHS: `h_Y(R_A(...)) = ...`
            *   RHS: `R_B(h_S(...), h_X(...)) = ...`
            *   LHS = RHS. The condition holds.

    *   **Case 2: ([State], [Input])**
        *   ...

    **5. Conclusion**

    The transition and output preservation conditions hold for all tested cases. Therefore, `h` is a valid homomorphism from `Z_A` to `Z_B`. [State any assumptions made].

    ---
    Now, generate a similar, rigorous homomorphism proof for the user-specified systems.
    """

    try:
        response = model.generate_content(final_prompt)
        # Add a basic check to see if the response looks like a proof
        if "Homomorphism Proof" not in response.text:
            raise ValueError("Generated text does not appear to be a valid proof.")
        
        # Add the generated proof to the conversation history
        conversation.add_artifact("morphism_proof", response.text)
        
        return response.text
    except Exception as e:
        print(f"ERROR in generate_morphism_proof: {e}")
        return f"### Error\nAn error occurred while generating the morphism proof. The AI may have generated an invalid response. Please try again with a more specific prompt.\n\n**Details:** {e}"

def generate_graph_from_text(conversation: Conversation) -> dict:
    """
    Generates a graph visualization from the full text of a Conversation object.
    """
    model = get_gemini_client()
    full_text = conversation.get_full_conversation_text()

    structured_prompt = f"""
    You are a systems engineering data visualization expert. Your task is to create a network graph from the provided text for a "{conversation.system_topic}".

    **Full Conversation Text:**
    ```
    {full_text}
    ```

    **Your Instructions:**
    1.  **Create Nodes:** Generate a node for each artifact (SR, SD, VR, VM). Each node needs an `id`, `label`, `group`, and `title`.
    2.  **Create Edges with Strict Hierarchy:** Analyze the text to create connections (edges) between the nodes. The connections MUST follow this strict hierarchical flow:
        -   **SDs connect to SRs:** An edge's `from` should be an SD, and its `to` should be an SR. The `label` should describe how the design implements the requirement (e.g., "implements").
        -   **VRs connect to SDs:** An edge's `from` should be a VR, and its `to` should be an SD. The `label` should be "verifies".
        -   **VMs connect to VRs:** An edge's `from` should be a VM, and its `to` should be a VR. The `label` should be "validates".
    3.  **Generate Graph Data:** Combine the nodes and edges into a `graph_data` object.
    4.  **Return JSON:** Your final output MUST be a single, valid JSON object containing only the `graph_data`.
    """

    try:
        response = model.generate_content(
            structured_prompt,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"ERROR in generate_graph_from_text: {e}")
        return {"graph_data": {"nodes": [{"id": "error", "label": "Graph Error", "title": str(e)}], "edges": []}}
