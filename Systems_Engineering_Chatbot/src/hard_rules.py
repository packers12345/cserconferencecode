import re
from typing import List, Dict, Any
from io import StringIO
# from .morphism_detector import Morphism # This will be imported only when needed for existing functionality.
from .isomorphism_graph_renderer import IsomorphismGraphRenderer
from .hardcoded_isomorphism_data import get_hardcoded_isomorphism_graph_data

"""
HARD-OVERRIDE RULES FOR SYSTEMS ENGINEERING CHATBOT

These rules take absolute precedence over all other prompt logic, default behavior, or system-design routines.
Routing is based on keyword detection. Responses must NEVER mix the two types, NEVER add PSF/SR logic,
and NEVER expand beyond what is explicitly required.

Rule 1: Mechanical Spring System Design Requests → Return System Z_A exactly.
Rule 2: RLC ↔ Mechanical Verification Requests → Return full 2nd-order morphism proof.
Rule 3: Visual Graph Requests → Return hardcoded isomorphism diagram.

FOLLOW-UP QUERY SUPPORT:
After a Rule 1, Rule 2, or Rule 3 response is delivered, users can ask follow-up questions that leverage the hardcoded
response combined with LLM analysis to provide deeper insights, derivations, and edge-case analysis.
Follow-up queries are routed to the LLM with the previous response as context.

IMPORTANT GUARDS:
- Rules MUST NEVER be mixed in a single response.
- PSF/SR (Problem Space / Solution Space) logic is STRICTLY FORBIDDEN in all rules.
- Initial responses are hardcoded and returned without LLM calls or synthesis engine involvement.
- Follow-up queries bypass the hardcoding and use LLM + context for deeper analysis.
- No requirement-space framing, no context manipulation, no expansion beyond specified structure for initial responses.
"""

# Guard: Ensure rules don't mix
_RULE_1_RESPONSE_MARKER = "System Z_A (Mechanical Spring System):"
_RULE_2_RESPONSE_MARKER = "PROBLEM: Assess whether a series RLC circuit"
_RULE_3_RESPONSE_MARKER = "<svg" # A simple marker for the SVG output

def _validate_no_mixing(response_text, rule_number):
    """
    Guard function: Ensure the response does not mix Rule 1, Rule 2, and Rule 3 content.
    Asserts that if we're returning Rule N, we don't contain other rule markers.
    """
    if rule_number == 1:
        assert _RULE_2_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 1 response contains Rule 2 marker. Rules must never mix."
        assert _RULE_3_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 1 response contains Rule 3 marker. Rules must never mix."
    elif rule_number == 2:
        assert _RULE_1_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 2 response contains Rule 1 marker. Rules must never mix."
        assert _RULE_3_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 2 response contains Rule 3 marker. Rules must never mix."
    elif rule_number == 3:
        assert _RULE_1_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 3 response contains Rule 1 marker. Rules must never mix."
        assert _RULE_2_RESPONSE_MARKER not in response_text, \
            "GUARD VIOLATION: Rule 3 response contains Rule 2 marker. Rules must never mix."


def _validate_no_psr_injection(response_text):
    """
    Guard function: Ensure PSF/SR (Problem Space / Solution Space) logic is not injected.
    Checks for common PSF/SR artifact markers and keywords that would violate the rules.
    """
    psr_markers = [
        "### SR-",      # System Requirements artifact
        "### SD-",      # System Design artifact
        "### VR-",      # Verification Requirement artifact
        "### VM-",      # Verification Model artifact
        "problem space",
        "solution space",
        "requirement",
        "stakeholder",
        "traceability"
    ]
    
    response_lower = response_text.lower()
    for marker in psr_markers:
        assert marker.lower() not in response_lower, \
            f"GUARD VIOLATION: PSF/SR logic detected ('{marker}'). Hard rules must not inject requirement-space framing."


def detect_rule_1_trigger(user_prompt):
    """
    Detect Rule 1 trigger keywords for Mechanical Spring System Design Requests.
    
    Trigger keywords include:
    - "create a system design for a mechanical spring system"
    - "mechanical spring system model"
    - "design the spring system"
    - "L1 model of spring"
    - "system Z spring"
    - "spring system design"
    - "mechanical system abstraction"
    
    Returns True if any trigger keyword is detected (case-insensitive substring match).
    """
    rule_1_keywords = [
        "create a system design for a mechanical spring system",
        "mechanical spring system model",
        "design the spring system",
        "l1 model of spring",
        "system z spring",
        "spring system design",
        "mechanical system abstraction",
    ]
    
    prompt_lower = user_prompt.lower()
    for keyword in rule_1_keywords:
        if keyword.lower() in prompt_lower:
            return True
    return False


def detect_rule_2_trigger(user_prompt):
    """
    Detect Rule 2 trigger keywords for RLC ↔ Mechanical Verification Requests.
    
    Trigger keywords include:
    - "assess whether an RLC can"
    - "RLC verify spring"
    - "RLC model spring system"
    - "mapping between RLC and spring"
    - "morphism between mechanical and electrical"
    - "structural equivalence RLC spring"
    - "homomorphism mechanical electrical"
    - "is the RLC equivalent to the mechanical system"
    - "analog model spring"
    - "verification model RLC"
    
    Returns True if any trigger keyword is detected (case-insensitive substring match).
    """
    rule_2_keywords = [
        "assess whether an RLC can",
        "RLC verify spring",
        "RLC model spring system",
        "mapping between RLC and spring",
        "morphism between mechanical and electrical",
        "structural equivalence RLC spring",
        "homomorphism mechanical electrical",
        "is the RLC equivalent to the mechanical system",
        "analog model spring",
        "verification model RLC",
    ]
    
    prompt_lower = user_prompt.lower()
    for keyword in rule_2_keywords:
        if keyword.lower() in prompt_lower:
            return True
    # Additional flexible patterns: detect prompts that ask to assess an RLC (with extra words)
    if "assess whether" in prompt_lower and "rlc" in prompt_lower:
        return True
    return False


def detect_morphism_graph_trigger(user_prompt: str) -> bool:
    """
    Detects Rule 3 trigger keywords for generating a hardcoded isomorphism graph.
    These are the keywords from SECTION 1 — TRIGGER SUPPRESSION.
    """
    trigger_keywords = [
        "create a visual graph",
        "create a visual",
        "create a diagram",
        "visual of the isomorphisms",
        "graph the isomorphisms",
        "draw the isomorphisms",
        "mapping graph",
        "isomorphism diagram",
        "system morphism graph",
        "mechanical and electrical isomorphisms visual"
    ]
    
    prompt_lower = user_prompt.lower()
    for keyword in trigger_keywords:
        if keyword.lower() in prompt_lower:
            return True
    return False


def is_followup_query(last_rule_triggered):
    """
    Determine if we should treat the current query as a follow-up to a previous hard rule response.
    This is a simple check: if the last interaction triggered a hard rule, any new non-triggering query
    is treated as a follow-up to that response.
    
    Args:
        last_rule_triggered: None, "rule_1", "rule_2", or "rule_3" from the conversation context
    
    Returns:
        True if we should route this as a follow-up query, False otherwise
    """
    return last_rule_triggered in ("rule_1", "rule_2", "rule_3")


def generate_rule_1_response():
    """
    RULE 1 — Return System Z_A exactly.
    
    Mechanical Spring System Design Response.
    This response must not introduce PSF/SR, must not add requirement-space logic,
    and must not expand beyond the exact structure specified.
    
    GUARDS ENFORCED:
    - No mixing with Rule 2 or Rule 3 content
    - No PSF/SR artifact markers or requirement-space framing
    - Response is exactly as specified, no LLM synthesis
    """
    response = """System Z_A (Mechanical Spring System):
• States:
  • Nondisplaced (x = 0, v = 0)
  • Displaced (Static): x ≠ 0, v = 0
  • Displaced (Dynamic): x ≠ 0, v ≠ 0
  • Optional Bounds: Max-Extension / Max-Compression (idealized limits)

• Input:
  • Force F(t)

• Outputs:
  • displacement x(t)
  • velocity v(t) = dx/dt

• Next State Function:
  Given current state (x, v) and input Force F(t):

  If F = 0:
  • If x = 0 and v = 0 → Nondisplaced
  • If x ≠ 0 and v = 0 → Displaced (Static)
  • If v ≠ 0 → Displaced (Dynamic)

  If F ≠ 0:
  • Any nonzero force produces displacement: next_state = Displaced (Dynamic)
  • NOTE: Under ideal physics, even arbitrarily small force causes motion.

• Structural Note:
  State variables (x, v) form the mechanical state vector. This aligns with the morphism to electrical systems (q, q')."""
    
    # Enforce guards
    _validate_no_mixing(response, rule_number=1)
    _validate_no_psr_injection(response)
    
    return response


def generate_rule_2_response():
    """
    RULE 2 — Return full 2nd-order morphism proof.
    
    RLC ↔ Mechanical Verification Response.
    Complete 2nd-order morphism proof using exact step-wise format.
    The assistant must always show all derivations, all algebraic steps, and all mapping checks.
    Must never shorten, summarize, or omit steps.
    
    GUARDS ENFORCED:
    - No mixing with Rule 1 or Rule 3 content
    - No PSF/SR artifact markers or requirement-space framing
    - Response is exactly as specified, no LLM synthesis
    - All 8 steps shown in full detail, no abbreviations
    """
    response = """PROBLEM: Assess whether a series RLC circuit can be leveraged as a verification model for a mechanical mass–spring–damper system.

STEP 0 — Problem statement and assumptions
Assume linear, time-invariant, lumped-parameter models.
Mechanical system includes mass m, damping c, stiffness k, input F(t), output x(t).
Electrical system includes inductance L, resistance R, capacitance C, input E(t), dependent variable q(t).

STEP 1 — Derive the 2nd-order Mechanical ODE (show all algebraic steps)
From Newton's law: F(t) - k x(t) - c x'(t) = m x''(t)
Standard form: m x''(t) + c x'(t) + k x(t) = F(t)
Characteristic equation: m r^2 + c r + k = 0
Transfer function: X(s)/F(s) = 1 / (m s^2 + c s + k)

STEP 2 — Derive the 2nd-order Electrical ODE (show all algebraic steps)
From KVL: E(t) - L q''(t) - R q'(t) - (1/C) q(t) = 0
Rearranged: L q''(t) + R q'(t) + (1/C) q(t) = E(t)
Characteristic equation: L r^2 + R r + 1/C = 0
Transfer function: Q(s)/E(s) = 1 / (L s^2 + R s + 1/C)

STEP 3 — Convert both systems to state-space form
Mechanical state variables: x1 = x, x2 = x'
Electrical state variables: z1 = q, z2 = q' (current)
Show both full A, B, C matrices explicitly, using the standard formulations:
Mechanical A = [[0, 1], [-k/m, -c/m]]
Electrical A = [[0, 1], [-1/(L C), -R/L]]
Mechanical B = [0; 1/m]
Electrical B = [0; 1/L]
Map outputs accordingly.

STEP 4 — Explicit morphism φ (structure-preserving mapping)
x ↔ q
x' ↔ q'
m ↔ L
c ↔ R
k ↔ 1/C
F(t) ↔ E(t)
Verify that substituting φ into the mechanical transfer function produces the electrical transfer function exactly.

STEP 5 — Damping ratio and natural frequency equivalence
Compute mechanical:
ω_n = sqrt(k/m)
ζ = c / (2 sqrt(m k))
Compute electrical:
ω_n = sqrt((1/C)/L)
ζ = R / (2) * sqrt(C/L)
Show explicitly that substituting m→L, c→R, k→1/C makes ζ_mech equal ζ_elec and ω_n_mech equal ω_n_elec.

STEP 6 — Initial condition mapping
Mechanical initial conditions: x(0) = x0, x'(0) = v0
Electrical initial conditions under φ: q(0) = x0, q'(0) = v0
Explain that linearity ensures solution equivalence.

STEP 7 — Optional impedance-level equivalence
Mechanical impedance: Z_mech = m s + c + k/s
Electrical impedance: Z_elec = L s + R + 1/(C s)
Explain that multiplication/division by s converts between force/velocity and voltage/current forms, confirming deeper equivalence.

STEP 8 — Conclusion rule
If differential equations, characteristic polynomials, state-space forms, transfer functions, damping ratios, and initial conditions all map under φ, conclude:
YES — The RLC circuit can be used as a verification model for the mechanical spring–mass–damper system.

Based on the complete structural equivalence demonstrated across all eight steps, and the perfect mapping of all parameters, differential equations, transfer functions, damping ratios, and initial conditions under the morphism φ:

YES — The RLC circuit can be used as a verification model for the mechanical spring–mass–damper system."""
    
    # Enforce guards
    _validate_no_mixing(response, rule_number=2)
    _validate_no_psr_injection(response)
    
    return response


def generate_hardcoded_morphism_graph_response() -> str:
    """
    RULE 3 — Generates the hardcoded isomorphism graph SVG and explanation.
    """
    data = get_hardcoded_isomorphism_graph_data()
    renderer = IsomorphismGraphRenderer()

    svg_content = renderer.render_static_isomorphism_graph_svg(
        nodes_data=data["nodes"],
        arcs_data=data["arcs"],
        explanation_text=data["explanation"],
        system1_name=data["system1_name"],
        system2_name=data["system2_name"]
    )
    
    # Enforce guards
    _validate_no_mixing(svg_content, rule_number=3)
    _validate_no_psr_injection(svg_content)

    return svg_content


def _detect_artifact_violation(response_text: str) -> bool:
    """
    Detects if the LLM response violates the guardrails by generating artifacts.
    
    Returns True if artifacts are detected, False if response is clean.
    """
    violation_markers = [
        "### SR-",      # System Requirements artifact
        "### SD-",      # System Design artifact
        "### VR-",      # Verification Requirement artifact
        "### VM-",      # Verification Model artifact
        "Verification Requirement",
        "Verification Model",
        "System Requirement",
        "System Design",
        "Problem Space",
        "Solution Space",
        "Verification Requirement (VR)",
        "Verification Model (VM)",
        "traceability matrix",
    ]
    
    response_lower = response_text.lower()
    for marker in violation_markers:
        if marker.lower() in response_lower:
            return True
    return False


def _sanitize_followup_response(response_text: str, user_prompt: str, previous_response: str) -> str:
    """
    Sanitizes LLM follow-up responses to ensure they comply with guardrails.
    
    If the response violates guardrails (e.g., generates artifacts), returns a 
    rejection message and offers a corrected re-prompt.
    
    Returns the sanitized response text.
    """
    if _detect_artifact_violation(response_text):
        return f"""[GUARDRAIL VIOLATION DETECTED]

Your previous response attempted to generate new artifacts or requirements, which violates the follow-up guidelines.

Follow-up Context:
- You are answering a question ABOUT an existing technical response.
- You must analyze and explain that existing response.
- You must NOT create new system models, requirements, or specifications.

Your Question Was:
{user_prompt}

Reference Material (what you should be analyzing):
{previous_response[:500]}...

Please provide a response that:
1. Directly references the above material
2. Explains, derives from, or explores deeper into that material
3. Does NOT generate new artifacts or requirements
4. Does NOT create new system models or verification frameworks"""
    
    return response_text


def generate_followup_with_guardrails(user_prompt: str, previous_response: str, last_rule: str, gemini_client):
    """
    Generate a follow-up response with strict guardrails to prevent artifact generation.
    
    This function routes follow-up queries to the LLM with a system prompt that:
    1. Forbids generation of any artifacts (SR, SD, VR, VM, specifications, requirements, designs)
    2. Forces the LLM to answer ONLY based on the provided context
    3. Prevents the LLM from synthesizing new requirements or designs
    4. Ensures the response is directly derived from the previous hard-coded response
    5. Detects and rejects responses that violate guardrails
    
    Parameters:
    - user_prompt: The user's follow-up question
    - previous_response: The exact hardcoded response (Rule 1, 2, or 3)
    - last_rule: Either "rule_1", "rule_2", or "rule_3"
    - gemini_client: The LLM client instance
    
    Returns:
    - Response text from the LLM, constrained to follow-up analysis only
    """
    
    # Determine the context header based on which rule was triggered
    if last_rule == "rule_1":
        context_header = "CONTEXT: System Z_A (Mechanical Spring System Design)"
        rule_label = "Rule 1 (Mechanical Spring System)"
    elif last_rule == "rule_2":
        context_header = "CONTEXT: RLC ↔ Mechanical Mass-Spring-Damper Morphism Proof"
        rule_label = "Rule 2 (RLC/Mechanical Verification)"
    else: # last_rule == "rule_3"
        context_header = "CONTEXT: Hardcoded Mechanical/Electrical Isomorphism Graph"
        rule_label = "Rule 3 (Isomorphism Graph)"
    
    # Compose the follow-up prompt with HARDENED EXPLICIT GUARDRAILS
    followup_prompt = f"""You are answering a follow-up question about a PREVIOUS technical response.
Your ONLY purpose is to analyze, explain, or derive deeper insights from that existing response.

{context_header}

Previous Response (must be used as the ONLY source for your answer):
========================================
{previous_response}
========================================

================== CRITICAL GUARDRAIL (ABSOLUTE RULES) ==================

WHAT YOU MUST DO:
✓ Answer based ONLY on the provided previous response
✓ Analyze, derive, or explain the content shown above
✓ Provide deeper technical insight or mathematical derivation
✓ Reference specific steps, equations, or concepts from the previous response
✓ If you cannot answer from the context, say explicitly: "This question cannot be answered from the provided context."

WHAT YOU ABSOLUTELY MUST NOT DO (FORBIDDEN):
✗ DO NOT generate any new artifacts (SR, SD, VR, VM, requirements, specifications, designs)
✗ DO NOT create new system models, verification models, or formal specifications
✗ DO NOT synthesize or invent content beyond the previous response
✗ DO NOT suggest traceability matrices, requirement traces, or verification frameworks
✗ DO NOT reformulate the problem or introduce new problem/solution space artifacts
✗ DO NOT create verification requirements or verification models
✗ DO NOT generate formal artifact headers (### SR-, ### SD-, ### VR-, ### VM-)
✗ DO NOT mention "Verification Requirement", "Verification Model", "Verification Framework"
✗ DO NOT structure output as new system engineering artifacts

EXAMPLES OF FORBIDDEN OUTPUTS (you will be rejected if you do this):
- "Verification Requirement (VR): [anything]"
- "Verification Model (VM): [anything]"
- "### VR-001: [anything]"
- "### VM-001: [anything]"
- New system definitions, requirements lists, or design specifications

YOUR RESPONSE MUST BE:
- Direct analysis or explanation of the previous content
- Derivation of equations or deeper mathematical insight
- Clarification or extension of concepts from the previous response
- Explicit statement if the question is outside the scope of provided context

User's Follow-up Question:
{user_prompt}

Generate your response now. Remember: analyze and explain the previous response, do not create new content."""
    
    try:
        if not gemini_client:
            return "Error: No AI client configured for follow-up analysis."
        
        # Send to LLM with the guardrailed prompt (NOT through synthesis engine)
        success, response_text = gemini_client.generate_content(followup_prompt)
        
        if not success:
            return f"Error: An error occurred during follow-up analysis: {response_text}"
        
        # SANITIZE: Check if response violates guardrails
        sanitized_response = _sanitize_followup_response(response_text, user_prompt, previous_response)
        return sanitized_response
        
    except Exception as e:
        print(f"ERROR in generate_followup_with_guardrails: {e}")
        return f"Error: An internal error occurred during follow-up generation: {e}"


def generate_any_followup_response(user_prompt: str, conversation, gemini_client):
    """
    Route ANY follow-up user prompt to the LLM with the last hard-coded response
    as background context, using strict guardrails to prevent artifact generation.
    
    No pertinence checks are performed - ALL follow-ups are routed directly to the LLM 
    with guardrailed instructions and the LLM decides how to respond based on context.
    
    conversation must be a Conversation instance.
    Returns the LLM response text, or None if no prior hard response available.
    """
    # Ensure conversation carries the last hard response
    prev_response = getattr(conversation, "last_hard_rule_response", None)
    last_rule = getattr(conversation, "last_rule_triggered", None)

    if not prev_response or not last_rule:
        return None  # Caller can fallback to normal routing if needed

    # Use the guardrailed follow-up function to prevent artifact generation
    return generate_followup_with_guardrails(user_prompt, prev_response, last_rule, gemini_client)
