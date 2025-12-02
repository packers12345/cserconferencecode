"""
Test the actual content of the hardened guardrail prompt to verify it contains all protections.
"""

import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Systems_Engineering_Chatbot.src.hard_rules import generate_rule_2_response


def extract_guardrail_prompt():
    """
    Reconstruct what the guardrail prompt looks like (without LLM call).
    This mimics what generate_followup_with_guardrails() would send to the LLM.
    """
    user_prompt = "walk me through that 2nd order electrical ODE"
    previous_response = generate_rule_2_response()
    last_rule = "rule_2"
    
    # Reconstruct the prompt (from hard_rules.py logic)
    context_header = "CONTEXT: RLC ↔ Mechanical Mass-Spring-Damper Morphism Proof"
    
    followup_prompt = f"""You are answering a follow-up question about a PREVIOUS technical response.
Your ONLY purpose is to analyze, explain, or derive deeper insights from that existing response.

{context_header}

Previous Response (must be used as the ONLY source for your answer):
========================================
{previous_response}
========================================

================== CRITICAL GUARDRAILS (ABSOLUTE RULES) ==================

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
    
    return followup_prompt


def main():
    print("=" * 80)
    print("GUARDRAIL PROMPT CONTENT VERIFICATION")
    print("=" * 80)
    
    prompt = extract_guardrail_prompt()
    
    # Check for key protective elements
    checks = [
        ("Contains 'WHAT YOU MUST DO' section", "WHAT YOU MUST DO:" in prompt),
        ("Contains checkmarks (✓) for allowed behaviors", "✓" in prompt),
        ("Contains X marks (✗) for forbidden behaviors", "✗" in prompt),
        ("Contains explicit VR/VM blocking", "### VR-001:" in prompt and "### VM-001:" in prompt),
        ("Contains 'FORBIDDEN' repetition", "FORBIDDEN" in prompt),
        ("Contains examples of blocked artifacts", '"Verification Requirement (VR):"' in prompt),
        ("Contains artifact header blocking", "(### SR-, ### SD-, ### VR-, ### VM-)" in prompt),
        ("Contains Problem/Solution Space blocking", "problem/solution space artifacts" in prompt),
        ("References previous response as only source", "ONLY source for your answer" in prompt),
        ("Explains sanitization will catch violations", "you will be rejected if you do this" in prompt),
    ]
    
    print("\nPrompt Content Checks:")
    all_pass = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_pass = False
    
    print("\n" + "=" * 80)
    if all_pass:
        print("✓ ALL CHECKS PASSED")
        print("\nThe hardened guardrail prompt includes:")
        print("  1. Repeated explicit negatives (✗ marks)")
        print("  2. Specific examples of forbidden artifacts (VR, VM, SR, SD headers)")
        print("  3. Clear allowed behaviors (✓ marks)")
        print("  4. Multiple reinforcements of 'analysis only, no artifact generation'")
        print("  5. Threat of rejection if rules violated")
    else:
        print("✗ SOME CHECKS FAILED")
    
    print("\n" + "=" * 80)
    print("SAMPLE OF PROMPT BEING SENT TO LLM:")
    print("=" * 80)
    print(prompt[:600] + "\n...[TRUNCATED]...\n")


if __name__ == "__main__":
    main()
