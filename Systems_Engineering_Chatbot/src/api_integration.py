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
    You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a formal mathematical proof of the existence of a homomorphism between a source system model (`$Z_A$`) and a target system model (`$Z_B$`). The proof must be narrative, rigorous, and adapt the structure of the example below to the specific systems provided.

    **User's Prompt:** "Create a homomorphism proof for a {{system_a_description}} and a {{system_b_description}}."

    **CRITICAL INSTRUCTIONS:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
    2.  **Define the Systems:** First, create plausible, formal definitions for both `$Z_A$` ({{system_a_description}}) and `$Z_B$` ({{system_b_description}}). Each system must be defined as a 5-tuple: `$(S, X, Y, N, R)$`. The states, inputs, and outputs should be relevant to the system's description.
    3.  **Define the Homomorphism:** Clearly define the three mapping functions: `$h_S$` (State Map), `$h_X$` (Input Map), and `$h_Y$` (Output Map). These mappings must be logical and consistent with the system definitions.
    4.  **Verify the Conditions:** Rigorously verify the two core conditions of a homomorphism for at least two representative state-input pairs. If a direct mapping is not possible, explain why and what assumptions are being made.
        *   **Transition Preservation:** `$h_S(N_A(s_A, x_A)) = N_B(h_S(s_A), h_X(x_A))$`
        *   **Output Preservation:** `$h_Y(R_A(s_A, x_A)) = R_B(h_S(s_A), h_X(x_A))$`
    5.  **Provide a Conclusion:** State whether the homomorphism is valid based on your verification, and clearly state any assumptions made during the proof.

    ---
    **EXAMPLE OF A RIGOROUS HOMOMORPHISM PROOF (ADAPT THIS STRUCTURE):**

    ### Homomorphism Proof: [System A] to [System B]

    This document provides a formal proof of the existence of a homomorphism `$h$` from a [System A] `$Z_A$` to a [System B] `$Z_B$`.

    **1. System $Z_A$ ([System A])**

    *   **States ($S_A$):** `$\\{s_{{A1}}: [State 1], s_{{A2}}: [State 2], ...\\}$`
    *   **Inputs ($X_A$):** `$\\{x_{{A1}}: [Input 1], x_{{A2}}: [Input 2], ...\\}$`
    *   **Outputs ($Y_A$):** `$\\{y_{{A1}}: [Output 1], y_{{A2}}: [Output 2], ...\\}$`
    *   **Next State Function ($N_A$):**
        *   `$N_A(s_{{A1}}, x_{{A1}}) = s_{{A2}}$`
        *   ...
    *   **Readout Function ($R_A$):**
        *   `$R_A(s_{{A2}}, x_{{A2}}) = y_{{A1}}$`
        *   ...

    **2. System $Z_B$ ([System B])**

    *   **States ($S_B$):** `$\\{s_{{B1}}: [State 1], s_{{B2}}: [State 2], ...\\}$`
    *   **Inputs ($X_B$):** `$\\{x_{{B1}}: [Input 1], x_{{B2}}: [Input 2], ...\\}$`
    *   **Outputs ($Y_B$):** `$\\{y_{{B1}}: [Output 1], y_{{B2}}: [Output 2], ...\\}$`
    *   **Next State Function ($N_B$):**
        *   `$N_B(s_{{B1}}, x_{{B1}}) = s_{{B2}}$`
        *   ...
    *   **Readout Function ($R_B$):**
        *   `$R_B(s_{{B2}}, x_{{B2}}) = y_{{B1}}$`
        *   ...

    **3. Define the Homomorphism `$h$`**

    *   **State Map ($h_S$):**
        *   `$h_S(s_{{A1}}) = s_{{B1}}$`
        *   ...
    *   **Input Map ($h_X$):**
        *   `$h_X(x_{{A1}}) = x_{{B1}}$`
        *   ...
    *   **Output Map ($h_Y$):**
        *   `$h_Y(y_{{A1}}) = y_{{B1}}$`
        *   ...

    **4. Verification of Conditions**

    *   **Case 1: ([State], [Input])**
        *   **Transition Preservation:**
            *   LHS: `$h_S(N_A(...)) = ...$`
            *   RHS: `$N_B(h_S(...), h_X(...)) = ...$`
            *   LHS = RHS. The condition holds.
        *   **Output Preservation:**
            *   LHS: `$h_Y(R_A(...)) = ...$`
            *   RHS: `$R_B(h_S(...), h_X(...)) = ...$`
            *   LHS = RHS. The condition holds.

    *   **Case 2: ([State], [Input])**
        *   ...

    **5. Conclusion**

    The transition and output preservation conditions hold for all tested cases. Therefore, `$h$` is a valid homomorphism from `$Z_A$` to `$Z_B$`. [State any assumptions made].

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

    **System X (Original System):** {{system_x_description}}
    **System Y (Replacement Model):** {{system_y_description}}

    **Instructions for Generating the Justification:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly, going into low-level mathematical detail for the isomorphic mappings.
    2.  **Start with the exact title:** "--- Justification: Isomorphic Mapping between {{system_x_description}} and {{system_y_description}} ---"
    3.  **Introduction to System Isomorphism and Wymorian System Theory:**
        *   Define a Wymorian System Model ($Z = (S, X, Y, N, R, F, P)$).
        *   Introduce homomorphism as a structure-preserving map between two systems ($Z_X$ and $Z_Y$) via mapping functions $h_S, h_X, h_Y$.
        *   Define isomorphism as a *bijective* homomorphism, implying a perfect, invertible structural and behavioral equivalence.
        *   Explain the "degree of homomorphism," with isomorphism representing the highest degree, allowing for direct interchangeability.
    4.  **Formal System Model for System X ({{system_x_description}}):**
        *   Provide a rigorous, formal definition for System X as a Wymorian System Model ($Z_X$).
        *   **States ($S_X$):** The set of internal states the system can occupy. For a mass-spring system, we consider its instantaneous position and velocity. $S_X = \\{{ (x(t), \\dot{{x}}(t)) \\}}$, where $x(t)$ is the displacement from equilibrium and $\\dot{{x}}(t)$ is the velocity. We can represent this as a state vector $\\mathbf{{s}}_X(t) = \\begin{{pmatrix}} x(t) \\\\ \\dot{{x}}(t) \\end{{pmatrix}}$.
        *   **Inputs ($X_X$):** The set of possible inputs to the system. $X_X = \\{{ F_{{ext}}(t), m, k \\}}$, where $F_{{ext}}(t)$ is the external applied force, $m$ is the mass, and $k$ is the spring constant (stiffness). We consider $m$ and $k$ as constant parameters influencing the dynamics, essentially constant inputs to the system's definition.
        *   **Outputs ($Y_X$):** The set of possible outputs from the system. $Y_X = \\{{ F_{{spring}}(t) \\}}$, where $F_{{spring}}(t)$ is the force exerted by the spring ($F_{{spring}}(t) = -k x(t)$).
        *   **Next State Function ($N_X$):** Governed by Newton's Second Law. The governing differential equation is: $m\\ddot{{x}}(t) + kx(t) = F_{{ext}}(t)$. To represent this in a first-order state-space form, let $s_{{X,1}}(t) = x(t)$ and $s_{{X,2}}(t) = \\dot{{x}}(t)$. Then:
            $$\\dot{{s}}_{{X,1}}(t) = s_{{X,2}}(t)$$
            $$\\dot{{s}}_{{X,2}}(t) = \\frac{{1}}{{m}}(F_{{ext}}(t) - k s_{{X,1}}(t))$$
            Thus, $N_X: S_X \\times X_X \\to S_X$ is given by $\\dot{{\\mathbf{{s}}}}_X(t) = N_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k) = \\begin{{pmatrix}} \\dot{{s}}_{{X,1}}(t) \\\\ \\dot{{s}}_{{X,2}}(t) \\end{{pmatrix}} = \\begin{{pmatrix}} s_{{X,2}}(t) \\\\ \\frac{{1}}{{m}}(F_{{ext}}(t) - k s_{{X,1}}(t)) \\end{{pmatrix}}$.
        *   **Readout Function ($R_X$):** The outputs are directly derived from the states and parameters: $R_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k) = F_{{spring}}(t) = -k x(t) = -k s_{{X,1}}(t)$.
        *   **Interfaces ($F_X, P_X$):**
            *   $F_X$: The spring provides a restoring force proportional to displacement. It stores potential energy.
            *   $P_X$: Physical connections for applying force, mounting the mass, and anchoring the spring.
    5.  **Formal System Model for System Y ({{system_y_description}}):**
        *   Provide a rigorous, formal definition for System Y as a Wymorian System Model ($Z_Y$).
        *   **States ($S_Y$):** The set of internal states the system can occupy. For an LC circuit, we consider the charge on the capacitor and the current flowing through the inductor (which is also the rate of change of charge). $S_Y = \\{{ (q(t), \\dot{{q}}(t)) \\}}$, where $q(t)$ is the charge on the capacitor and $\\dot{{q}}(t) = i(t)$ is the current. We represent this as a state vector $\\mathbf{{s}}_Y(t) = \\begin{{pmatrix}} q(t) \\\\ i(t) \\end{{pmatrix}}$.
        *   **Inputs ($X_Y$):** The set of possible inputs to the system. $X_Y = \\{{ V_{{ext}}(t), L, C \\}}$, where $V_{{ext}}(t)$ is the external applied voltage (source), $L$ is the inductance, and $C$ is the capacitance. We consider $L$ and $C$ as constant parameters.
        *   **Outputs ($Y_Y$):** The set of possible outputs from the system. $Y_Y = \\{{ V_{{cap}}(t) \\}}$, where $V_{{cap}}(t)$ is the voltage across the capacitor ($V_{{cap}}(t) = \\frac{{1}}{{C}} q(t)$).
        *   **Next State Function ($N_Y$):** Governed by Kirchhoff's Voltage Law (KVL). For a series LC circuit, the sum of voltage drops is equal to the applied voltage: $L\\ddot{{q}}(t) + \\frac{{1}}{{C}}q(t) = V_{{ext}}(t)$. To represent this in a first-order state-space form, let $s_{{Y,1}}(t) = q(t)$ and $s_{{Y,2}}(t) = \\dot{{q}}(t) = i(t)$. Then:
            $$\\dot{{s}}_{{Y,1}}(t) = s_{{Y,2}}(t)$$
            $$\\dot{{s}}_{{Y,2}}(t) = \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} s_{{Y,1}}(t))$$
            Thus, $N_Y: S_Y \\times X_Y \\to S_Y$ is given by $\\dot{{\\mathbf{{s}}}}_Y(t) = N_Y(\\mathbf{{s}}_Y(t), V_{{ext}}(t), L, C) = \\begin{{pmatrix}} \\dot{{s}}_{{Y,1}}(t) \\\\ \\dot{{s}}_{{Y,2}}(t) \\end{{pmatrix}} = \\begin{{pmatrix}} s_{{Y,2}}(t) \\\\ \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} s_{{Y,1}}(t)) \\end{{pmatrix}}$.
        *   **Readout Function ($R_Y$):** The outputs are directly derived from the states and parameters: $R_Y(\\mathbf{{s}}_Y(t), V_{{ext}}(t), L, C) = V_{{cap}}(t) = \\frac{{1}}{{C}} q(t) = \\frac{{1}}{{C}} s_{{Y,1}}(t)$.
        *   **Interfaces ($F_Y, P_Y$):**
            *   $F_Y$: The capacitor stores electric field energy, and the inductor stores magnetic field energy. They regulate current and voltage.
            *   $P_Y$: Electrical terminals for connecting components and applying voltage sources.
    6.  **Establishing the Isomorphic Mapping (Low-Level Detail)**

    To demonstrate isomorphism, we must define bijective mapping functions $h_S, h_X, h_Y$ and show they preserve the functional structures of $N$ and $R$.
    6.1. Define the Bijective Mapping Functions

    These mappings establish the one-to-one correspondence between the quantities of the mechanical system and the electrical system.

    *   **State Map ($h_S$):**
        *   $h_S(x(t)) = q(t)$ (Mechanical displacement maps to Electrical charge)
        *   $h_S(\\dot{{x}}(t)) = \\dot{{q}}(t) = i(t)$ (Mechanical velocity maps to Electrical current)
        This mapping is bijective as position and velocity are uniquely mapped to charge and current, and vice-versa, assuming a continuous, smooth time-domain.

    *   **Input Map ($h_X$):**
        *   $h_X(F_{{ext}}(t)) = V_{{ext}}(t)$ (External mechanical force maps to External electrical voltage)
        *   $h_X(m) = L$ (Mechanical mass maps to Electrical inductance)
        *   $h_X(k) = 1/C$ (Mechanical spring constant maps to Inverse of Electrical capacitance)
        This mapping is bijective, as each mechanical input/parameter has a unique electrical counterpart, and vice-versa.

    *   **Output Map ($h_Y$):**
        *   $h_Y(F_{{spring}}(t)) = h_Y(-k x(t))$ which implies, using the parameter and state maps, $h_Y(-k x(t)) = -(1/C) q(t) = -V_{{cap}}(t)$. Thus, $h_Y(F_{{spring}}(t)) = -V_{{cap}}(t)$ (Spring force maps to Capacitor voltage, with a sign convention depending on how the force/voltage is defined relative to the state). This mapping is bijective due to the bijective nature of the underlying state and parameter maps.

    6.2. Demonstrate Preservation of Next State Function (N)

    We need to show that applying the state and input maps to System X's next state function yields System Y's next state function. Formally, $h_S(N_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k)) = N_Y(h_S(\\mathbf{{s}}_X(t)), h_X(F_{{ext}}(t)), h_X(m), h_X(k))$.

    Start with the System X next state function (in state-space form):
    $$\\dot{{\\mathbf{{s}}}}_X(t) = N_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k) = \\begin{{pmatrix}} \\dot{{x}}(t) \\\\ \\frac{{1}}{{m}}(F_{{ext}}(t) - k x(t)) \\end{{pmatrix}}$$

    Apply the state map $h_S$ to the components of $\\dot{{\\mathbf{{s}}}}_X(t)$ and substitute variables and parameters according to $h_S$ and $h_X$ definitions:
    $$h_S(\\dot{{\\mathbf{{s}}}}_X(t)) = \\begin{{pmatrix}} h_S(\\dot{{x}}(t)) \\\\ h_S\\left(\\frac{{1}}{{m}}(F_{{ext}}(t) - k x(t))\\right) \\end{{pmatrix}}$$

    For the first component: $h_S(\\dot{{x}}(t)) = \\dot{{q}}(t) = i(t)$.
    For the second component, we apply the constitutive mappings:
    $$h_S\\left(\\frac{{1}}{{m}}(F_{{ext}}(t) - k x(t))\\right) = \\frac{{1}}{{h_X(m)}}(h_X(F_{{ext}}(t)) - h_X(k) h_S(x(t)))$$
    $$= \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} q(t))$$
    Therefore, the expression $\\dot{{\\mathbf{{s}}}}_X(t)$ transforms to $\\begin{{pmatrix}} i(t) \\\\ \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} q(t)) \\end{{pmatrix}}$. This transformation relies on the algebraic structure being preserved across the mapped quantities.

    Resulting transformed vector:
    $$h_S(N_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k)) = \\begin{{pmatrix}} i(t) \\\\ \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} q(t)) \\end{{pmatrix}}$$

    Compare with the System Y next state function:
    Recall System Y's next state function:
    $$N_Y(h_S(\\mathbf{{s}}_X(t)), h_X(F_{{ext}}(t)), h_X(m), h_X(k)) = N_Y(\\begin{{pmatrix}} q(t) \\\\ i(t) \\end{{pmatrix}}, V_{{ext}}(t), L, \\frac{{1}}{{C}}) = \\begin{{pmatrix}} i(t) \\\\ \\frac{{1}}{{L}}(V_{{ext}}(t) - \\frac{{1}}{{C}} q(t)) \\end{{pmatrix}$$

    Since the transformed $N_X$ is identical to $N_Y$, we have rigorously demonstrated the preservation of the next state function: $h_S(N_X(\\mathbf{{s}}_X(t), x_X)) = N_Y(h_S(\\mathbf{{s}}_X(t)), h_X(x_X))$.

    6.3. Demonstrate Preservation of Readout Function (R)

    We need to show that $h_Y(R_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k)) = R_Y(h_S(\\mathbf{{s}}_X(t)), h_X(F_{{ext}}(t)), h_X(m), h_X(k))$.

    Start with the System X readout function:
    $$R_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k) = -k x(t)$$

    Apply the output map $h_Y$ to the components:
    $$h_Y(R_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k)) = h_Y(-k x(t))$$

    For $h_Y(-k x(t))$, we use the defined parameter and state mappings: $h_X(k) = 1/C$ and $h_S(x(t)) = q(t)$. So, $h_Y(-k x(t)) = -(1/C) q(t) = -V_{{cap}}(t)$. Note: $F_{{spring}}(t)$ is generally defined as the force exerted by the spring, which opposes displacement ($-kx(t)$). The analogous electrical quantity, capacitor voltage $V_{{cap}}(t)$, also represents a "restoring" effect. If we define $F_{{spring}}(t)$ as the force on the spring, $F_{{spring}}(t) = -kx(t)$, then the mapping is $h_Y(F_{{spring}}(t)) = -V_{{cap}}(t)$. The consistency holds.

    Resulting transformed vector:
    $$h_Y(R_X(\\mathbf{{s}}_X(t), F_{{ext}}(t), m, k)) = -V_{{cap}}(t)$$

    Compare with the System Y readout function:
    Recall System Y's readout function:
    $$R_Y(h_S(\\mathbf{{s}}_X(t)), h_X(F_{{ext}}(t)), h_X(m), h_X(k)) = R_Y(\\begin{{pmatrix}} q(t) \\\\ i(t) \\end{{pmatrix}}, V_{{ext}}(t), L, \\frac{{1}}{{C}}) = \\frac{{1}}{{C}} q(t) = V_{{cap}}(t)$$

    Assuming consistent sign conventions for $F_{{spring}}(t)$ and $V_{{cap}}(t)$ (e.g., $F_{{spring}}(t)$ is the reaction force from the spring, and $V_{{cap}}(t)$ is the voltage across the capacitor), the functional forms are preserved. The mapping $h_Y(F_{{spring}}(t)) = -V_{{cap}}(t)$ with suitable sign adjustments confirms this.

    This demonstrates the preservation of the readout function.
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

    **User's Prompt:** "Create a homomorphic proof for a {{system_x_description}} and a {{system_y_description}}, and quantify the degree of homomorphism across the two systems."

    **CRITICAL INSTRUCTIONS:**
    1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
    2.  **Define the Systems:** First, create plausible, formal definitions for both `$Z_X$` ({{system_x_description}}) and `$Z_Y$` ({{system_y_description}}). Each system must be defined as a 5-tuple: `$(S, X, Y, N, R)$`. The states, inputs, and outputs should be relevant to the system's description.
    3.  **Define the Homomorphism:** Clearly define the three mapping functions: `$h_S$` (State Map), `$h_X$` (Input Map), and `$h_Y$` (Output Map). These mappings must be logical and consistent with the system definitions.
    4.  **Verify the Conditions:** Rigorously verify the two core conditions of a homomorphism for at least two representative state-input pairs. If a direct mapping is not possible, explain why and what assumptions are being made.
        *   **Transition Preservation:** `$h_S(N_X(s_X, x_X)) = N_Y(h_S(s_X), h_X(x_X))$`
        *   **Output Preservation:** `$h_Y(R_X(s_X, x_X)) = R_Y(h_S(s_X), h_X(x_X))$`
    5.  **Quantify Degree of Homomorphism:**
        *   Based on Wymorian Systems Theory, explain what the "degree of homomorphism" means in this context, including its mathematical interpretation (e.g., ratio of preserved properties, cardinality of mapped elements, error metrics).
        *   Discuss how well the defined mappings preserve the structure and behavior, providing specific examples from the verification steps.
        *   Provide a qualitative assessment (e.g., "high degree," "partial," "strong isomorphism") and justify it based on the rigor of the mathematical mappings and the extent of property preservation. This justification *must* be explicitly driven by the mathematical and system theory principles of Wymorian proof, detailing how the mappings and verified conditions directly support the quantified degree.
        *   Offer a system theory-based justification for the chosen quantification, referencing concepts like behavioral equivalence, structural similarity, and the implications for system replacement or modeling within the Wymorian framework.
        *   If it's an isomorphism, explicitly state it and explain why (bijective mappings, perfect preservation of all relevant system properties and dynamics), grounding this explanation in Wymorian System Theory.
    6.  **Provide a Conclusion:** State whether the homomorphism is valid based on your verification, and clearly state any assumptions made during the proof and the final quantified degree of homomorphism.

    ---
    **EXAMPLE OF A RIGOROUS HOMOMORPHISM PROOF (ADAPT THIS STRUCTURE):**

    ### Homomorphism Proof: [System X] to [System Y]

    This document provides a formal proof of the existence of a homomorphism `$h$` from a [System X] `$Z_X$` to a [System Y] `$Z_Y$`.

    **1. System $Z_X$ ([System X])**

    *   **States ($S_X$):** `$\\{s_{{X1}}: [State 1], s_{{X2}}: [State 2], ...\\}$`
    *   **Inputs ($X_X$):** `$\\{x_{{X1}}: [Input 1], x_{{X2}}: [Input 2], ...\\}$`
    *   **Outputs ($Y_X$):** `$\\{y_{{X1}}: [Output 1], y_{{X2}}: [Output 2], ...\\}$`
    *   **Next State Function ($N_X$):**
        *   `$N_X(s_{{X1}}, x_{{X1}}) = s_{{X2}}$`
        *   ...
    *   **Readout Function ($R_X$):**
        *   `$R_X(s_{{X2}}, x_{{X2}}) = y_{{X1}}$`
        *   ...

    **2. System $Z_Y$ ([System Y])**

    *   **States ($S_Y$):** `$\\{s_{{Y1}}: [State 1], s_{{Y2}}: [State 2], ...\\}$`
    *   **Inputs ($X_Y$):** `$\\{x_{{Y1}}: [Input 1], x_{{Y2}}: [Input 2], ...\\}$`
    *   **Outputs ($Y_Y$):** `$\\{y_{{Y1}}: [Output 1], y_{{Y2}}: [Output 2], ...\\}$`
    *   **Next State Function ($N_Y$):**
        *   `$N_Y(s_{{Y1}}, x_{{Y1}}) = s_{{Y2}}$`
        *   ...
    *   **Readout Function ($R_Y$):**
        *   `$R_Y(s_{{Y2}}, x_{{Y2}}) = y_{{Y1}}$`
        *   ...

    **3. Define the Homomorphism `$h$`**

    *   **State Map ($h_S$):**
        *   `$h_S(s_{{X1}}) = s_{{Y1}}$`
        *   ...
    *   **Input Map ($h_X$):**
        *   `$h_X(x_{{X1}}) = x_{{Y1}}$`
        *   ...
    *   **Output Map ($h_Y$):**
        *   `$h_Y(y_{{X1}}) = y_{{Y1}}$`
        *   ...

    **4. Verification of Conditions**

    *   **Case 1: ([State], [Input])**
        *   **Transition Preservation:**
            *   LHS: `$h_S(N_X(...)) = ...$`
            *   RHS: `$N_Y(h_S(...), h_X(...)) = ...$`
            *   LHS = RHS. The condition holds.
        *   **Output Preservation:**
            *   LHS: `$h_Y(R_X(...)) = ...$`
            *   RHS: `$R_Y(h_S(...), h_X(...)) = ...$`
            *   LHS = RHS. The condition holds.

    *   **Case 2: ([State], [Input])**
        *   ...

    **5. Quantification of Degree of Homomorphism**

    [Explain the degree of homomorphism, qualitative assessment, and justification here.]

    **6. Conclusion**

    The transition and output preservation conditions hold for all tested cases. Therefore, `$h$` is a valid homomorphism from `$Z_X$` to `$Z_Y$`. [State any assumptions made]. The degree of homomorphism is [Quantified Degree].

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
    You are a systems engineering data visualization expert. Your task is to create a network graph from the provided text for a "{{conversation.system_topic}}".

    **Full Conversation Text:**
    ```
    {{full_text}}
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
            return {{"graph_data": {{"nodes": [{{"id": "error", "label": "Graph Error", "title": str(e)}}], "edges": []}}}}
    
    return {{"graph_data": {{"nodes": [{{"id": "error", "label": "Graph Error", "title": f"Failed to generate graph after {max_retries} attempts due to persistent API errors."}}], "edges": []}}}}
