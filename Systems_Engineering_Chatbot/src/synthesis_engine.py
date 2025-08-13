import os
import json
from api_integration import get_gemini_client
from pdf_processor import extract_tables_from_pdf

class SynthesisEngine:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.gemini_client = None  # Lazy load this

    def generate_response(self, prompt: str, conversation_context: dict) -> str:
        """
        Generates a Wymorian-based algebraic structure for a given system.
        """
        if self.gemini_client is None:
            self.gemini_client = get_gemini_client()

        system_topic = conversation_context.get("system_topic", "the specified system")

        wymorian_prompt = f"""
        You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a single, formal algebraic structure for a user-specified system based on the principles in Dr. Wach's dissertation. Your response must be descriptive, narrative, and strictly follow the detailed examples provided below.

        **User's Prompt:** "{prompt}"
        **System Topic:** {system_topic}

        **CRITICAL INSTRUCTIONS:**
        1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
        2.  **Identify the Artifact:** Based on the user's prompt, determine which single WySE artifact to create (SR, SD, VR, or VM).
        3.  **Follow the Narrative Format:** Your output must be a detailed, explanatory, markdown-formatted response. It must not just list components, but explain them in the context of the system, precisely mirroring the style, depth, and formalisms of the examples.

        ---
        **EXAMPLE 1: System Requirements (SR) Response**

        ### 1. System Requirements (SR) as a Problem Space of Functions (PSF)
        First, we formalize the system requirements for the **{system_topic}** into a **Problem Space of Functions (PSF)**. This defines the *what* by specifying the required transformations of inputs to outputs, bounded by performance constraints, without dictating implementation.
        Let's define the superset SR, which is an instantiation of a PSF: **SR = (X, Y, XY, P, F)**
        - **A. Items of Exchange (IoX): Inputs (X) and Outputs (Y)**
          - **Inputs (X):** `x_mission_parameters` (e.g., Payload, Destination), `x_system_constraints` (e.g., Airspace, Battery).
          - **Outputs (Y):** `y_mission_status` (e.g., Confirmation, Log), `y_performance_data` (e.g., Speed, Altitude).
        - **B. Transformation Functions (XY):** This set defines the required performance. For instance: `XY_1: (x_mission_parameters) → y_performance_data.Speed`, ensuring Speed ≥ 25 m/s.
        - **C. Interfaces (P, F):** These define how the system interacts with the world, e.g., a `Mission_Control_Interface` for receiving `x_mission_parameters`.
        This formalization ensures every requirement is unambiguous, testable, and part of a coherent whole.

        ---
        **EXAMPLE 2: System Design (SD) Response**

        ### 2. System Design (SD) as a System Model (SM)
        A System Design (SD) is a proposed solution that must exist within the bounds of the SR's Problem Space. We can formalize a design, such as a specific implementation for the **{system_topic}**, as a Level 1 System Model (`Z_SD1`).
        **Z_SD1 = (S, X, Y, N, R, P, F)**
        - **States (S):** The set of operational states, e.g., `{{s_idle, s_ascending, s_cruising, s_delivering, s_returning}}`.
        - **Inputs (X):** The specific inputs the design accepts, e.g., `{{x_mission_plan, x_lidar_data, x_gps_data}}`.
        - **Outputs (Y):** The specific outputs the design produces, e.g., `{{y_motor_rpms, y_winch_command, y_flight_log}}`.
        - **Next State Function (N):** The logic that governs state transitions, e.g., a function `n_1: ((s_idle, x_mission_plan), s_ascending)`.
        - **Readout Function (R):** The function that maps states to outputs, e.g., `r_1: (s_cruising) → y_motor_rpms`.
        This SD1 is considered a valid solution because it can be mathematically proven to adhere to the SR's problem space.

        ---
        **EXAMPLE 3: Verification Requirement (VR) and Verification Model (VM) Response**

        ### 3. Verification Requirement (VR) and Verification Model (VM)
        Now, let's define a verification activity for a key requirement of the **{system_topic}**.
        **A. Verification Requirement (VR)**
        As per Wach, a VR is a combination of a **Verification Requirement Problem Space (VRPS)** and **Verification Model Morphic Conditions (VMMC)**.
        - **VRPS1 (Wind Tunnel Test):** A simplified problem space to bound the test.
          - **Inputs (X_VRPS1):** `(W_p, wind_speed)`
          - **Outputs (Y_VRPS1):** `v_measured`
          - **Transformation (XY_VRPS1):** `(W_p, wind_speed) → v_measured`, where `v_measured ≥ 25 m/s`.
        - **VMMC1 (Desired Pedigree):** Defines required representativeness.
          - "The VM must have a **parameter isomorphism** to the SD's propulsion system with respect to `{{thrust, drag_coefficient}}`."
        **B. Verification Model (VM)**
        A potential VM is a physical scale model for a wind tunnel.
        - **Verification Model (VM1):** A 1:2 scale model of the drone's airframe with identical motors.
        This VM1 is formalized as another System Model, `Z_VM1`. We can then mathematically prove that `Z_VM1` adheres to `VRPS1` and satisfies `VMMC1`.

        ---
        Now, generate the appropriate WySE artifact in a similar narrative style for the user's prompt about **{system_topic}**.
        """

        try:
            response = self.gemini_client.generate_content(wymorian_prompt)
            return response.text
        except Exception as e:
            print(f"ERROR in SynthesisEngine: {e}")
            return f"### Error\nAn error occurred during synthesis: {e}"

    def generate_traceability_matrix(self, system_topic: str) -> str:
        """
        Generates a complete, deterministic Wymorian Traceability Matrix from a single prompt.
        """
        if self.gemini_client is None:
            self.gemini_client = get_gemini_client()

        matrix_prompt = f"""
        You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a complete, mathematically rigorous traceability matrix for the given system topic. You must first self-generate a plausible set of requirements, design elements, and verification artifacts, and then use them to construct the full traceability report.

        **System Topic:** {system_topic}

        **CRITICAL INSTRUCTIONS:**
        1.  **Self-Generate Artifacts:** First, create a plausible set of 3-4 system requirements (SR), 3-4 design elements (SD), and 3-4 verification artifacts (VR/VM) for the system topic. Assign unique IDs to each (e.g., r1, d1, v1).
        2.  **Strictly Adhere to Format:** The final output must be a single markdown document that strictly follows the four sections in the example below: "1. Define the Sets", "2. Formal Requirement Representations", "3. Traceability Relations", and "4. Bidirectional Traceability Check".
        3.  **Be Deterministic:** The entire response must be generated in a single, coherent block. Do not rely on external information or previous prompts.

        ---
        **EXAMPLE OF FINAL OUTPUT STRUCTURE:**

        ### Wymorian Traceability Matrix for: [System Topic]

        **1. Define the Sets**
        *   **Requirements Set (R):**
            *   `r1`: [Full text of requirement 1]
            *   `r2`: [Full text of requirement 2]
            *   ...
        *   **Design Set (D):**
            *   `d1`: [Full text of design element 1]
            *   `d2`: [Full text of design element 2]
            *   ...
        *   **Verification Artifacts Set (V):**
            *   `v1`: [Full text of verification artifact 1]
            *   `v2`: [Full text of verification artifact 2]
            *   ...

        **2. Formal Requirement Representations**
        *   `r1`: [Formal logic representation of r1, e.g., ∀p ∈ Payload, p ≤ 5kg]
        *   `r2`: [Formal logic representation of r2]
        *   ...

        **3. Traceability Relations**
        *   **Requirement-to-Design (T₁ ⊆ R × D):** `[('r1', 'd1'), ('r2', 'd2'), ...]`
        *   **Requirement-to-Verification (T₂ ⊆ R × V):** `[('r1', 'v1'), ('r2', 'v2'), ...]`
        *   **Design-to-Verification (T₃ ⊆ D × V):** `[('d1', 'v1'), ('d2', 'v2'), ...]`

        **4. Bidirectional Traceability Check**
        *   **Completeness:** Every requirement `rᵢ` is implemented by at least one design artifact `dⱼ` and verified by at least one verification artifact `vₖ`.
            *   `r1` → `d1`, `v1` (Pass)
            *   `r2` → `d2`, `v2` (Pass)
            *   ...
        *   **Consistency:** Every design artifact `dⱼ` is covered by a verification artifact `vₖ`.
            *   `d1` → `v1` (Pass)
            *   `d2` → `v2` (Pass)
            *   ...
        ---

        Now, generate the complete Wymorian Traceability Matrix for the **{system_topic}**.
        """

        try:
            response = self.gemini_client.generate_content(matrix_prompt)
            return response.text
        except Exception as e:
            print(f"ERROR in SynthesisEngine matrix generation: {e}")
            return f"### Error\nAn error occurred during matrix generation: {e}"

if __name__ == '__main__':
    # This is for testing purposes.
    pdf_file_path = os.path.join(os.path.dirname(__file__), '..', 'Wach_PF_D_2023 (1).pdf')
    
    engine = SynthesisEngine(pdf_file_path)

    # Example prompt and context
    test_prompt = "what is the verification requirements for a drone delivery system"
    test_context = {
        "system_topic": "drone delivery system",
    }

    # Generate a response
    generated_response = engine.generate_response(test_prompt, test_context)
    print("Generated Response:\n", generated_response)
