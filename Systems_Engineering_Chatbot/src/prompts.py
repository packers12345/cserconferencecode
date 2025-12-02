"""
This module stores all the prompt templates used for interacting with the Gemini API.
    Separating prompts from the application logic makes them easier to manage, test, and update.
"""

def get_homomorphism_proof_prompt(system_a_description: str, system_b_description: str) -> str:
    """
    Generates a formal mathematical proof of the existence of a homomorphism.
    """
    return f"""
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

def get_isomorphism_justification_prompt(system_x_description: str, system_y_description: str, morphism_proof_context: str = "") -> str:
    """
    Generates a comprehensive justification for why a system Y can be used to replace a system X.
    Includes an optional morphism_proof_context for additional structured information.
    """
    morphism_context_section = ""
    if morphism_proof_context:
        morphism_context_section = f"""
**Structured Morphism Proof Context:**
```
{morphism_proof_context}
```
When generating the justification, you MUST refer to this context for mathematical formulas, variable correspondences, and symbolic states related to the mass-spring-damper and RLC circuit systems. Specifically, use the table provided in the context for variable correspondence.
"""

    return f"""
You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to generate a comprehensive justification for why a system Y (the model) can be used to replace a system X (the original system). This justification must be rigorously based on the principles of homomorphic mapping, isomorphism, the degree of homomorphism, and Wymorian System Theory.

{morphism_context_section}

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
    *   **Referencing `Structured Morphism Proof Context`:** When defining mappings and demonstrating preservation, explicitly refer to the mathematical formulas, variable correspondences, and symbolic states provided in the `Structured Morphism Proof Context` if available and relevant to {system_x_description} and {system_y_description}.
    *   **Define the Bijective Mapping Functions:**
        *   **State Map (h_S):** `h_S: S_X -> S_Y`. Explicitly define the mapping for each state variable.
        *   **Input Map (h_X):** `h_X: X_X -> X_Y`. Explicitly define the mapping for each input variable.
        *   **Output Map (h_Y):** `h_Y: Y_X -> Y_Y`. Explicitly define the mapping for each output variable.
        *   **Parameter Isomorphism:** Explicitly state the one-to-one correspondence of parameters, leveraging the provided variable correspondence table if applicable.
    *   **Demonstrate Preservation of Next State Function (N):**
        *   Present `N_X` for System X.
        *   Apply `h_S` and `h_X` to `N_X`, substituting variables and parameters according to the defined mappings (referencing the context's variable correspondence).
        *   Demonstrate that the transformed equation is exactly `N_Y`. This rigorously proves `h_S(N_X(s_X, x_X)) = N_Y(h_S(s_X), h_X(x_X))`.
    *   **Demonstrate Preservation of Readout Function (R):**
        *   Present `R_X` for System X.
        *   Apply `h_Y` and `h_S` (and parameter isomorphism) to show how this maps to an analogous `R_Y` output. Explain the direct correspondence, again leveraging the context for variable mappings.
7.  **Justification via Wymorian System Theory:**
    *   Conclude by explicitly stating that because a *bijective homomorphism* (an isomorphism) has been demonstrated at a low mathematical level, Wymorian System Theory dictates that these systems are behaviorally equivalent.
    *   Reiterate the implications: predictive power, design analogy, and formal justification for interchangeability.
    *   Emphasize that this rigorous mapping confirms the highest "degree of homomorphism."
8.  **Properties Leading to Isomorphism:**
    *   Identify and explain the underlying physical or abstract properties, system requirements, and design choices for both System X and System Y that enable this isomorphic relationship.
    *   Explain how these shared properties are crucial for establishing the bijective mappings and preserving the system dynamics.
"""

def get_graph_generation_prompt(system_topic: str, full_text: str) -> str:
    """
    Generates a network graph from the provided text.
    """
    return f"""
You are a systems engineering data visualization expert. Your task is to create a network graph from the provided text for a "{system_topic}".

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

def get_l1_mapping_prompt(system_a: str, system_b: str) -> str:
    """
    Produces a structured L1 mapping between two abstract system models in a narrative format.
    """
    return f"""
You are a world-class expert in Wymorian Systems Engineering (WySE) and systems theory. Your task is to generate a comprehensive L1 mapping between two abstract system models, System A and System B, in a detailed narrative format. The response must include all relevant mathematical artifacts and follow the structure provided in the example.

**System A:** {system_a}
**System B:** {system_b}

**CRITICAL INSTRUCTIONS:**
1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
2.  **Start with the exact title:** "### L1 Mapping: {system_a} to {system_b}"
3.  **System Definitions:** Briefly define both System A and System B.
4.  **Variable and Parameter Mapping:**
    *   Clearly list the corresponding dynamic variables (e.g., displacement ↔ charge) and system parameters (e.g., mass ↔ inductance).
    *   Use the format: "Mechanical Displacement (`x`) ↔ Electrical Charge (`q`)"
5.  **Governing Equations:**
    *   Present the fundamental governing equations for both System A and System B.
    *   Use standard mathematical notation.
6.  **Algebraic Proof of Structure Preservation:**
    *   Provide a step-by-step algebraic substitution.
    *   Start with the governing equation of System A.
    *   Apply the defined mappings to transform System A's equation into System B's equation.
    *   Clearly state that this demonstrates the preservation of the system's mathematical structure.
7.  **Impedance/Transfer Forms (Laplace Domain):**
    *   Show the analogous forms in the Laplace domain (or similar relevant domain).
    *   Present the impedance or transfer function for both systems.
8.  **Validity Conditions:**
    *   List the assumptions and conditions under which this L1 mapping is valid (e.g., ideal components, linear behavior, specific configurations).
9.  **Conclusion:** Summarize the significance of the L1 mapping, emphasizing the structural and behavioral equivalence.

---
**EXAMPLE OF A NARRATIVE L1 MAPPING (ADAPT THIS STRUCTURE):**

### L1 Mapping: Mechanical Spring-Mass-Damper System to Series RLC Circuit

This L1 mapping establishes a formal correspondence between a mechanical spring-mass-damper system and a series RLC circuit, demonstrating their structural and behavioral equivalence under specific conditions.

**1. System Definitions**

*   **Mechanical Spring-Mass-Damper System:** This system consists of a mass (`m`) attached to a spring with spring constant (`k`) and a damper with damping coefficient (`b`), subjected to an external force (`F(t)`). Its primary dynamic variable is displacement (`x`).
*   **Series RLC Circuit:** This circuit comprises a resistor (`R`), an inductor (`L`), and a capacitor (`C`) connected in series, driven by a voltage source (`V(t)`). Its primary dynamic variable is charge (`q`).

**2. Variable and Parameter Mapping**

The L1 mapping identifies the following equivalences between the two systems:

*   **Dynamic Variables:**
    *   Mechanical Displacement (`x`) ↔ Electrical Charge (`q`)
    *   Mechanical Velocity (`v = dx/dt`) ↔ Electrical Current (`i = dq/dt`)
*   **System Parameters:**
    *   Mechanical Mass (`m`) ↔ Electrical Inductance (`L`)
    *   Mechanical Damping Coefficient (`b`) ↔ Electrical Resistance (`R`)
    *   Mechanical Spring Constant (`k`) ↔ Inverse Electrical Capacitance (`1/C`)
*   **Driving Forces:**
    *   Mechanical Force (`F(t)`) ↔ Electrical Voltage (`V(t)`)

**3. Governing Equations**

The dynamic behavior of each system is described by a second-order linear ordinary differential equation:

*   **Mechanical System (Newton's Second Law):**
    `m * (d^2x/dt^2) + b * (dx/dt) + k * x = F(t)`

*   **Electrical System (Kirchhoff's Voltage Law):**
    `L * (d^2q/dt^2) + R * (dq/dt) + (1/C) * q = V(t)`

**4. Algebraic Proof of Structure Preservation**

To demonstrate the L1 mapping, we substitute the mechanical variables and parameters with their electrical counterparts into the mechanical system's governing equation:

Starting with the mechanical equation:
`m * (d^2x/dt^2) + b * (dx/dt) + k * x = F(t)`

Applying the mappings:
*   Replace `m` with `L`
*   Replace `b` with `R`
*   Replace `k` with `1/C`
*   Replace `x` with `q`
*   Replace `F(t)` with `V(t)`

The equation transforms into:
`L * (d^2q/dt^2) + R * (dq/dt) + (1/C) * q = V(t)`

This transformed equation is precisely the governing equation for the series RLC circuit, thereby proving the preservation of the system's mathematical structure under this L1 mapping.

**5. Impedance/Transfer Forms (Laplace Domain)**

In the Laplace domain, assuming zero initial conditions, the transfer functions (or impedance forms) also show direct correspondence:

*   **Mechanical System (Impedance):**
    `Z_mechanical(s) = m*s^2 + b*s + k`

*   **Electrical System (Impedance):`
    `Z_electrical(s) = L*s^2 + R*s + 1/C`

The direct analogy in their polynomial forms further reinforces the L1 mapping.

**6. Validity Conditions**

This L1 mapping is valid under the following assumptions:

*   Both the mechanical spring-mass-damper system and the series RLC circuit are assumed to exhibit linear behavior.
*   The spring, damper, resistor, inductor, and capacitor are considered ideal components.
*   The mechanical system operates within small displacements where the spring force is linearly proportional to displacement.
*   The RLC circuit is a series configuration.

**7. Conclusion**

In conclusion, the L1 mapping rigorously demonstrates that a mechanical spring-mass-damper system and a series RLC circuit are isomorphic at this level of abstraction, meaning they share the same fundamental dynamic behavior, allowing for insights from one domain to be directly applied to the other.
"""

def get_single_system_extraction_prompt(system_name: str, expert_documentation: str = "") -> str:
    """
    Generates a prompt for the LLM to extract a complete mathematical specification for a single system.
    """
    documentation_context = ""
    if expert_documentation:
        documentation_context = f"""
**Expert Documentation for {system_name} System:**
```
{expert_documentation}
```
When extracting the specification for "{system_name}", you MUST leverage this documentation to accurately identify and extract its components (Input, Output, State Variables, State Function, Transfer Function, Interface), their mathematical forms, and relevant parameters. Specifically, refer to the differential equations, variable correspondences, and state/interface descriptions provided.
"""

    return f"""
Extract complete mathematical specification for system: "{system_name}"

{documentation_context}

REQUIRED FIELDS (return ONLY valid JSON, no markdown):

{{
    "system_name": "{system_name}",
    "input": {{
        "symbol": "e.g., F(t), V(t), u(t)",
        "description": "Brief description of input",
        "domain": "e.g., ℝ → ℝ, ℤ → ℝ",
        "units": "e.g., Newtons, Volts",
        "equation": "Mathematical definition",
        "constraints": "Any constraints on input"
    }},
    "output": {{
        "symbol": "e.g., x(t), q(t), y(t)",
        "description": "Brief description of output",
        "domain": "e.g., ℝ → ℝ",
        "units": "e.g., meters, Coulombs",
        "equation": "Mathematical definition",
        "constraints": "Any constraints"
    }},
    "state_variables": {{
        "symbols": ["x1", "x2", ...],
        "descriptions": ["description1", "description2", ...],
        "dimension": integer,
        "vector_form": "[x1; x2; ...] notation"
    }},
    "next_state_function": {{
        "equations": "Differential equations or recurrence relations",
        "matrix_form": "d/dt x = Ax + Bu or similar",
        "A_matrix": "Matrix as string representation",
        "B_vector": "Input matrix as string",
        "coefficients": {{"param1": "meaning1", "param2": "meaning2"}},
        "order": "e.g., 2nd order",
        "system_type": "e.g., Linear Time-Invariant (LTI)"
    }},
    "transfer_function": {{
        "symbolic_form": "G(s) = numerator/denominator",
        "numerator": [coefficient list],
        "denominator": [coefficient list],
        "poles": "pole locations",
        "zeros": "zero locations",
        "DC_gain": float,
        "order": "system order"
    }} or null,
    "interface": {{
        "input_coupling": "How input is coupled to system",
        "output_measurement": "How output is measured",
        "boundary_conditions": ["Initial condition 1", "Initial condition 2"],
        "energy_expression": "Energy equation if applicable"
    }}
}}

Be precise and technical. Include ALL mathematical details. Return VALID JSON ONLY.
"""

def get_synthesis_prompt(prompt: str, system_topic: str) -> str:
    """
    Generates a prompt for the LLM to create a Wymorian-based algebraic structure.
    """
    return f"""
You are a world-class expert in Wymorian Systems Engineering (WySE). Your task is to analyze the user's prompt related to "{system_topic}" and generate a Wymorian-based algebraic structure, system requirements, or other relevant systems engineering artifact.

**User Prompt:** "{prompt}"

**CRITICAL INSTRUCTIONS:**
1.  **Adopt the Persona:** You are a systems engineering professor. Explain the concepts clearly, formally, and thoroughly.
2.  **Generate Relevant Artifact:** Based on the user's prompt, generate a relevant Wymorian artifact. This could be:
    *   A formal definition of a Wymorian System Model (Z = (S, X, Y, N, R, F, P)).
    *   A set of system requirements (SR).
    *   A system design (SD).
    *   Verification requirements (VR).
    *   A verification model (VM).
3.  **Ensure Rigor:** All generated content must be mathematically rigorous and adhere to Wymorian principles.
4.  **Provide Explanation:** Clearly explain the generated artifact and its components.
5.  **Use Markdown:** Format your response using clear markdown headings and bullet points.

---
Now, generate the Wymorian artifact based on the user's prompt.
"""

def get_traceability_matrix_prompt(system_topic: str) -> str:
    """
    Generates a complete, deterministic Wymorian Traceability Matrix from a single prompt.
    """
    return f"""
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

def get_morphism_proof_prompt_template(formatted_morphism_proof: str) -> str:
    """
    Provides a structured morphism proof as context for the LLM.
    """
    return f"""
You are a world-class expert in Wymorian Systems Engineering (WySE) and systems theory. You have been provided with a structured resource detailing the morphism proof between a mass-spring-damper system and an RLC circuit.

**Structured Morphism Proof Resource:**
```
{formatted_morphism_proof}
```

**Your Task:**
When asked about the morphism between a mass-spring-damper system and an RLC circuit, or related concepts like their mathematical analogy, variable correspondence, or symbolic states, you MUST refer to the provided "Structured Morphism Proof Resource".

Use this resource to:
1.  **Explain the analogy:** Describe how the governing differential equations are mathematically analogous.
2.  **Detail variable correspondence:** Clearly list the mappings between mechanical and electrical variables and parameters.
3.  **Describe symbolic states:** Explain the symbolic states for both systems as defined in the resource (Mechanical: Nondisplaced, Displaced; Electrical: Underdamped, Overdamped, Critically Damped).
4.  **Elaborate on state interfaces:** Use the provided descriptions for mechanical and electrical system states, inputs, outputs, and next state functions.

Ensure your responses are formal, rigorous, and directly leverage the information from the "Structured Morphism Proof Resource" to provide accurate and consistent explanations. Do not invent information not present in the resource.
"""


def get_isomorphism_extraction_prompt(system_1_description: str, system_2_description: str, expert_documentation: str = "") -> str:
    """
    Generates a prompt that instructs the LLM to analyze two systems and extract:
    1. Component nodes for each system (inputs, outputs, transfer functions, state functions, interfaces)
    2. Morphism mappings (edges) between corresponding components
    3. Confidence scores for each morphism
    4. Structured JSON output with nodes, morphisms, and reasoning
    
    Returns strict JSON suitable for graph visualization.
    """
    documentation_context = ""
    if expert_documentation:
        documentation_context = f"""
**Expert Documentation for Mechanical Spring and RLC Circuit Systems:**
```
{expert_documentation}
```
When analyzing "mechanical spring system" or "RLC circuit", you MUST leverage this documentation to accurately identify and extract their components (Input, Output, State Variables, State Function, Transfer Function, Interface), their mathematical forms, and relevant parameters. Specifically, refer to the differential equations, variable correspondences, and state/interface descriptions provided.
"""
    return f"""
You are a systems engineer performing structural isomorphism analysis on two systems.

Your task: Analyze the two systems below and extract a complete isomorphism graph showing component-level mappings.

SYSTEM 1 DESCRIPTION:
{system_1_description}

SYSTEM 2 DESCRIPTION:
{system_2_description}

{documentation_context}

STEP 1: COMPONENT IDENTIFICATION
For each system, identify and extract the following component types (create one node per component):
- INPUT: What drives the system? (list all inputs)
- OUTPUT: What does the system produce? (list all outputs)
- TRANSFER FUNCTION: Mathematical relationship between input and output
- STATE FUNCTION: Internal state representation (state variables, equations)
- INTERFACE: System parameters and their roles

STEP 2: NODE POSITIONING
Assign preliminary positions to nodes:
- System 1 nodes: x in range [50, 250]
- System 2 nodes: x in range [550, 750]
- All nodes: y values spread [50, 450] (different y for different component types)

STEP 3: MORPHISM DETECTION
For each component pair (across systems), determine if a morphism exists:
- Do both systems have corresponding inputs? How similar are they?
- Do both systems have corresponding outputs? How similar are they?
- Are transfer functions structurally equivalent or similar?
- Are state vectors dimensionally or structurally equivalent?
- Do interface parameters play analogous roles?

STEP 4: MORPHISM CHARACTERIZATION
For each morphism, assign:
- morphism_type: one of ["1-to-1", "many-to-1", "1-to-many", "structural_isomorphism", "parameter_mapping", "partial"]
- confidence: number between 0.0 and 1.0 (1.0 = certain, 0.0 = no morphism)
- reasoning: brief explanation of why this morphism exists or doesn't exist

STEP 5: OUTPUT STRICTLY FORMATTED JSON (NO PROSE BEFORE OR AFTER)

Return ONLY valid JSON matching this exact structure. No preamble, no explanation, only the JSON:

{{
  "systems": [
    {{
      "system_id": "system_1",
      "system_name": "System 1 Name",
      "nodes": [
        {{
          "node_id": "input_1",
          "node_type": "input",
          "label": "Input Name",
          "mathematical_form": "Mathematical expression or description",
          "position": {{"x": 50, "y": 50}}
        }},
        {{
          "node_id": "output_1",
          "node_type": "output",
          "label": "Output Name",
          "mathematical_form": "Mathematical expression or description",
          "position": {{"x": 250, "y": 50}}
        }},
        {{
          "node_id": "tf_1",
          "node_type": "transfer_function",
          "label": "Transfer Function",
          "mathematical_form": "Transfer function equation",
          "position": {{"x": 150, "y": 200}}
        }},
        {{
          "node_id": "state_1",
          "node_type": "state_function",
          "label": "State Representation",
          "mathematical_form": "State vector or state equation",
          "position": {{"x": 150, "y": 300}}
        }},
        {{
          "node_id": "interface_1",
          "node_type": "interface",
          "label": "System Parameters/Interface",
          "mathematical_form": "Parameter list and roles",
          "position": {{"x": 150, "y": 400}}
        }}
      ]
    }},
    {{
      "system_id": "system_2",
      "system_name": "System 2 Name",
      "nodes": [
        {{"node_id": "input_2", "node_type": "input", "label": "Input Name", "mathematical_form": "...", "position": {{"x": 550, "y": 50}}}},
        {{"node_id": "output_2", "node_type": "output", "label": "Output Name", "mathematical_form": "...", "position": {{"x": 750, "y": 50}}}},
        {{"node_id": "tf_2", "node_type": "transfer_function", "label": "Transfer Function", "mathematical_form": "...", "position": {{"x": 650, "y": 200}}}},
        {{"node_id": "state_2", "node_type": "state_function", "label": "State Representation", "mathematical_form": "...", "position": {{"x": 650, "y": 300}}}},
        {{"node_id": "interface_2", "node_type": "interface", "label": "System Parameters/Interface", "mathematical_form": "...", "position": {{"x": 650, "y": 400}}}}
      ]
    }}
  ],
  "morphisms": [
    {{
      "morphism_id": "morph_input",
      "from_node": "input_1",
      "to_node": "input_2",
      "morphism_type": "1-to-1",
      "confidence": 0.95,
      "reasoning": "Both serve as driving inputs to their respective systems."
    }},
    {{
      "morphism_id": "morph_output",
      "from_node": "output_1",
      "to_node": "output_2",
      "morphism_type": "1-to-1",
      "confidence": 0.90,
      "reasoning": "Both represent the primary system output."
    }},
    {{
      "morphism_id": "morph_tf",
      "from_node": "tf_1",
      "to_node": "tf_2",
      "morphism_type": "structural_isomorphism",
      "confidence": 0.98,
      "reasoning": "Transfer functions have identical 2nd-order form with parameter mapping: param1↔param2, param3↔param4."
    }},
    {{
      "morphism_id": "morph_state",
      "from_node": "state_1",
      "to_node": "state_2",
      "morphism_type": "1-to-1",
      "confidence": 0.92,
      "reasoning": "State vectors are dimensionally equivalent and represent analogous quantities."
    }},
    {{
      "morphism_id": "morph_interface",
      "from_node": "interface_1",
      "to_node": "interface_2",
      "morphism_type": "parameter_mapping",
      "confidence": 0.96,
      "reasoning": "System parameters map as follows: mass↔inductance, damping↔resistance, stiffness↔inverse-capacitance."
    }}
  ],
  "overall_assessment": {{
    "is_isomorphic": true,
    "isomorphism_type": "full_structural_isomorphism",
    "summary": "The two systems exhibit complete structural isomorphism across all component types."
  }}
}}

Remember: Output ONLY the JSON. No explanations, no preamble. The JSON must be valid and parseable.
"""
