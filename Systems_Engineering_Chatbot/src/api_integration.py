import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
from dotenv import load_dotenv
import sys
import os

# Add the directory containing context_manager.py to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from context_manager import Conversation

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def get_gemini_client():
    """Configures and returns a Gemini client."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file.")
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel('models/gemini-2.5-flash')

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

    retries = 0
    max_retries = 5
    base_delay = 1  # seconds

    while retries < max_retries:
        try:
            response = model.generate_content(final_prompt)
            # Add a basic check to see if the response looks like a proof
            if "Homomorphism Proof" not in response.text:
                raise ValueError("Generated text does not appear to be a valid proof.")
            
            # Add the generated proof to the conversation history
            conversation.add_artifact("morphism_proof", response.text)
            
            return response.text
        except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
            retries += 1
            delay = base_delay * (2 ** (retries - 1))
            print(f"Rate limit or API error encountered: {e}. Retrying in {delay} seconds (attempt {retries}/{max_retries}).")
            time.sleep(delay)
        except Exception as e:
            print(f"ERROR in generate_morphism_proof: {e}")
            return f"### Error\nAn error occurred while generating the morphism proof. The AI may have generated an invalid response. Please try again with a more specific prompt.\n\n**Details:** {e}"
    
    return f"### Error\nFailed to generate morphism proof after {max_retries} attempts due to persistent API errors."

def generate_isomorphism_justification(system_x_description: str, system_y_description: str) -> str:
    """
    Generates a detailed justification for why system Y can replace system X based on
    homomorphic mapping, isomorphism, degree of homomorphism, and Wymorian system theory.
    """
    model = get_gemini_client()

    justification_prompt = f"""
    You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a comprehensive justification for why a system Y (the model) can be used to replace a system X (the original system). This justification must be rigorously based on the principles of homomorphic mapping, isomorphism, the degree of homomorphism, and Wymorian System Theory.

    **System X (Original System):** {system_x_description}
    **System Y (Replacement Model):** {system_y_description}

    **Instructions for Generating the Justification:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly, going into low-level mathematical detail for the isomorphic mappings.
    2.  **Start with the exact title:** "--- Justification: Isomorphic Mapping between {system_x_description} and {system_y_description} ---"
    3.  **Introduction to System Isomorphism and Wymorian System Theory:**
        *   Define a Wymorian System Model (Z = (S, X, Y, N, R, F, P)).
        *   Introduce homomorphism as a structure-preserving map between two systems (Z_X and Z_Y) via mapping functions h_S, h_X, h_Y.
        *   Define isomorphism as a *bijective* homomorphism, implying a perfect, invertible structural and behavioral equivalence.
        *   Explain the "degree of homomorphism," with isomorphism representing the highest degree, allowing for direct interchangeability.
    4.  **Formal System Model for System X ({system_x_description}):**
        *   Provide a rigorous, formal definition for System X as a Wymorian System Model (Z_X).
        *   **States (S_X):** Define as a set of state variables relevant to System X.
        *   **Inputs (X_X):** Define as a set of input variables for System X. Also include system parameters as inputs to the model's behavior.
        *   **Outputs (Y_X):** Define as a set of output variables for System X.
        *   **Next State Function (N_X):** Explicitly state the governing differential equation(s) or rules for System X. Explain how this defines the transition from current states to next states.
        *   **Readout Function (R_X):** Explicitly state how outputs are derived from states and inputs for System X.
        *   **Interfaces (F_X, P_X):** Briefly mention physical and functional interfaces.
    5.  **Formal System Model for System Y ({system_y_description}):**
        *   Provide a rigorous, formal definition for System Y as a Wymorian System Model (Z_Y).
        *   **States (S_Y):** Define as a set of state variables relevant to System Y.
        *   **Inputs (X_Y):** Define as a set of input variables for System Y. Also include system parameters.
        *   **Outputs (Y_Y):** Define as a set of output variables for System Y.
        *   **Next State Function (N_Y):** Explicitly state the governing differential equation(s) or rules for System Y. Explain how this defines the transition from current states to next states.
        *   **Readout Function (R_Y):** Explicitly state how outputs are derived from states and inputs for System Y.
        *   **Interfaces (F_Y, P_Y):** Briefly mention physical and functional interfaces.
    6.  **Establishing the Isomorphic Mapping (Low-Level Detail):**
        *   **Define the Bijective Mapping Functions:**
            *   **State Map (h_S):** `h_S: S_X -> S_Y`. Explicitly define the mapping for each state variable.
            *   **Input Map (h_X):** `h_X: X_X -> X_Y`. Explicitly define the mapping for each input variable.
            *   **Output Map (h_Y):** `h_Y: Y_X -> Y_Y`. Explicitly define the mapping for each output variable.
            *   **Parameter Isomorphism:** Explicitly state the one-to-one correspondence of parameters.
        *   **Demonstrate Preservation of Next State Function (N):**
            *   Present `N_X` for System X.
            *   Apply `h_S` and `h_X` to `N_X`, substituting variables and parameters according to the defined mappings.
            *   Demonstrate that the transformed equation is exactly `N_Y`. This rigorously proves `h_S(N_X(s_X, x_X)) = N_Y(h_S(s_X), h_X(x_X))`.
        *   **Demonstrate Preservation of Readout Function (R):**
            *   Present `R_X` for System X.
            *   Apply `h_Y` and `h_S` (and parameter isomorphism) to show how this maps to an analogous `R_Y` output. Explain the direct correspondence.
    7.  **Justification via Wymorian System Theory:**
        *   Conclude by explicitly stating that because a *bijective homomorphism* (an isomorphism) has been demonstrated at a low mathematical level, Wymorian System Theory dictates that these systems are behaviorally equivalent.
        *   Reiterate the implications: predictive power, design analogy, and formal justification for interchangeability.
        *   Emphasize that this rigorous mapping confirms the highest "degree of homomorphism."
    8.  **Properties Leading to Isomorphism:**
        *   Identify and explain the underlying physical or abstract properties, system requirements, and design choices for both System X and System Y that enable this isomorphic relationship.
        *   Explain how these shared properties are crucial for establishing the bijective mappings and preserving the system dynamics.
    """

    retries = 0
    max_retries = 5
    base_delay = 1  # seconds

    while retries < max_retries:
        try:
            response = model.generate_content(justification_prompt)
            if "Justification: " not in response.text:
                raise ValueError("Generated text does not appear to be a valid justification.")
            return response.text
        except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
            retries += 1
            delay = base_delay * (2 ** (retries - 1))
            print(f"Rate limit or API error encountered: {e}. Retrying in {delay} seconds (attempt {retries}/{max_retries}).")
            time.sleep(delay)
        except Exception as e:
            print(f"ERROR in generate_isomorphism_justification: {e}")
            return f"### Error\nAn error occurred while generating the isomorphism justification. Details: {e}"
    
    return f"### Error\nFailed to generate isomorphism justification after {max_retries} attempts due to persistent API errors."

def generate_homomorphic_proof_and_quantification(conversation: Conversation, system_y_description: str) -> str:
    """
    Generates a homomorphic proof for system X and system Y, and quantifies the degree of homomorphism.
    Leverages Wymorian Systems Theory and isomorphic mapping properties.
    """
    model = get_gemini_client()
    system_x_description = conversation.system_topic

    homomorphic_proof_prompt = f"""
    You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to create a formal homomorphic proof for System X and System Y, and then quantify the degree of homomorphism across the two systems.

    **User's Prompt:** "Create a homomorphic proof for a {system_x_description} and a {system_y_description}, and quantify the degree of homomorphism across the two systems."

    **CRITICAL INSTRUCTIONS:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
    2.  **Define the Systems:** First, create plausible, formal definitions for both `Z_X` ({system_x_description}) and `Z_Y` ({system_y_description}). Each system must be defined as a 5-tuple: `(S, X, Y, N, R)`. The states, inputs, and outputs should be relevant to the system's description.
    3.  **Define the Homomorphism:** Clearly define the three mapping functions: `h_S` (State Map), `h_X` (Input Map), and `h_Y` (Output Map). These mappings must be logical and consistent with the system definitions.
    4.  **Verify the Conditions:** Rigorously verify the two core conditions of a homomorphism for at least two representative state-input pairs. If a direct mapping is not possible, explain why and what assumptions are being made.
        *   **Transition Preservation:** `h_S(N_X(s_X, x_X)) = N_Y(h_S(s_X), h_X(x_X))`
        *   **Output Preservation:** `h_Y(R_X(s_X, x_X)) = R_Y(h_S(s_X), h_X(x_X))`
    5.  **Quantify Degree of Homomorphism:**
        *   Based on Wymorian Systems Theory, explain what the "degree of homomorphism" means in this context, including its mathematical interpretation (e.g., ratio of preserved properties, cardinality of mapped elements, error metrics).
        *   Discuss how well the defined mappings preserve the structure and behavior, providing specific examples from the verification steps.
        *   Provide a qualitative assessment (e.g., "high degree," "partial," "strong isomorphism") and justify it based on the rigor of the mathematical mappings and the extent of property preservation.
        *   Offer a system theory-based justification for the chosen quantification, referencing concepts like behavioral equivalence, structural similarity, and the implications for system replacement or modeling.
        *   If it's an isomorphism, explicitly state it and explain why (bijective mappings, perfect preservation of all relevant system properties and dynamics).
    6.  **Provide a Conclusion:** State whether the homomorphism is valid based on your verification, and clearly state any assumptions made during the proof and the final quantified degree of homomorphism.

    ---
    **EXAMPLE OF A RIGOROUS HOMOMORPHISM PROOF (ADAPT THIS STRUCTURE):**

    ### Homomorphism Proof: [System X] to [System Y]

    This document provides a formal proof of the existence of a homomorphism `h` from a [System X] `Z_X` to a [System Y] `Z_Y`.

    **1. System Z_X ([System X])**

    *   **States (S_X):** `{{s_X1: [State 1], s_X2: [State 2], ...}}`
    *   **Inputs (X_X):** `{{x_X1: [Input 1], x_X2: [Input 2], ...}}`
    *   **Outputs (Y_X):** `{{y_X1: [Output 1], y_X2: [Output 2], ...}}`
    *   **Next State Function (N_X):**
        *   `N_X(s_X1, x_X1) = s_X2`
        *   ...
    *   **Readout Function (R_X):**
        *   `R_X(s_X2, x_X2) = y_X1`
        *   ...

    **2. System Z_Y ([System Y])**

    *   **States (S_Y):** `{{s_Y1: [State 1], s_Y2: [State 2], ...}}`
    *   **Inputs (X_Y):** `{{x_Y1: [Input 1], x_Y2: [Input 2], ...}}`
    *   **Outputs (Y_Y):** `{{y_Y1: [Output 1], y_Y2: [Output 2], ...}}`
    *   **Next State Function (N_Y):**
        *   `N_Y(s_Y1, x_Y1) = s_Y2`
        *   ...
    *   **Readout Function (R_Y):**
        *   `R_Y(s_Y2, x_Y2) = y_Y1`
        *   ...

    **3. Define the Homomorphism `h`**

    *   **State Map (h_S):**
        *   `h_S(s_X1) = s_Y1`
        *   ...
    *   **Input Map (h_X):**
        *   `h_X(x_X1) = x_Y1`
        *   ...
    *   **Output Map (h_Y):**
        *   `h_Y(y_X1) = y_Y1`
        *   ...

    **4. Verification of Conditions**

    *   **Case 1: ([State], [Input])**
        *   **Transition Preservation:**
            *   LHS: `h_S(N_X(...)) = ...`
            *   RHS: `N_Y(h_S(...), h_X(...)) = ...`
            *   LHS = RHS. The condition holds.
        *   **Output Preservation:**
            *   LHS: `h_Y(R_X(...)) = ...`
            *   RHS: `R_Y(h_S(...), h_X(...)) = ...`
            *   LHS = RHS. The condition holds.

    *   **Case 2: ([State], [Input])**
        *   ...

    **5. Quantification of Degree of Homomorphism**

    [Explain the degree of homomorphism, qualitative assessment, and justification here.]

    **6. Conclusion**

    The transition and output preservation conditions hold for all tested cases. Therefore, `h` is a valid homomorphism from `Z_X` to `Z_Y`. [State any assumptions made]. The degree of homomorphism is [Quantified Degree].

    ---
    Now, generate a similar, rigorous homomorphic proof for the user-specified systems, including the quantification of the degree of homomorphism.
    """

    retries = 0
    max_retries = 5
    base_delay = 1  # seconds

    while retries < max_retries:
        try:
            response = model.generate_content(homomorphic_proof_prompt)
            if "Homomorphism Proof" not in response.text:
                raise ValueError("Generated text does not appear to be a valid homomorphic proof.")
            
            conversation.add_artifact("homomorphic_proof_quantification", response.text)
            
            return response.text
        except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
            retries += 1
            delay = base_delay * (2 ** (retries - 1))
            print(f"Rate limit or API error encountered: {e}. Retrying in {delay} seconds (attempt {retries}/{max_retries}).")
            time.sleep(delay)
        except Exception as e:
            print(f"ERROR in generate_homomorphic_proof_and_quantification: {e}")
            return f"### Error\nAn error occurred while generating the homomorphic proof and quantification. Details: {e}"
    
    return f"### Error\nFailed to generate homomorphic proof and quantification after {max_retries} attempts due to persistent API errors."


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

    retries = 0
    max_retries = 5
    base_delay = 1  # seconds

    while retries < max_retries:
        try:
            response = model.generate_content(
                structured_prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
            retries += 1
            delay = base_delay * (2 ** (retries - 1))
            print(f"Rate limit or API error encountered: {e}. Retrying in {delay} seconds (attempt {retries}/{max_retries}).")
            time.sleep(delay)
        except Exception as e:
            print(f"ERROR in generate_graph_from_text: {e}")
            return {"graph_data": {"nodes": [{"id": "error", "label": "Graph Error", "title": str(e)}], "edges": []}}
    
    return {"graph_data": {"nodes": [{"id": "error", "label": "Graph Error", "title": f"Failed to generate graph after {max_retries} attempts due to persistent API errors."}], "edges": []}}
