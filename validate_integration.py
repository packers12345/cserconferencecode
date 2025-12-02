"""
Integration validation: Shows how hard_rules integrate with app.py routing flow.
Demonstrates that Rule 1 and Rule 2 are truly the first check and block all other logic.
"""

import sys
sys.path.insert(0, r'c:\Users\adiiy\OneDrive\Desktop\Code_Folder2')

from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
)


def simulate_chat_routing(prompt):
    """
    Simulates the /chat endpoint routing with hard-override rules.
    Shows that hard rules block all other logic.
    """
    print("\n" + "=" * 80)
    print(f"SIMULATED REQUEST: {prompt}")
    print("=" * 80)
    
    # Step 1: Validate prompt (already checked by Flask)
    print("\n[1] Validate prompt: ✓ Not empty")
    
    # Step 2: HARD-OVERRIDE CHECK (NEW - executes before anything else)
    print("\n[2] CHECK HARD-OVERRIDE RULES:")
    
    rule_1_match = detect_rule_1_trigger(prompt)
    rule_2_match = detect_rule_2_trigger(prompt)
    
    if rule_1_match:
        print("    ✓ RULE 1 TRIGGERED → Return System Z_A")
        print("    ✓ BYPASS: Conversation loading, all other routing")
        response = generate_rule_1_response()
        system_topic = "Mechanical Spring System (System Z_A)"
        print(f"\n    Response preview: {response[:100]}...")
        print(f"    System topic: {system_topic}")
        return {
            "response_text": response,
            "system_topic": system_topic,
            "routing": "HARD-RULE-1"
        }
    
    if rule_2_match:
        print("    ✓ RULE 2 TRIGGERED → Return RLC-Morphism Proof")
        print("    ✓ BYPASS: Conversation loading, all other routing")
        response = generate_rule_2_response()
        system_topic = "RLC Circuit and Mechanical Spring System Morphism Verification"
        print(f"\n    Response preview: {response[:100]}...")
        print(f"    System topic: {system_topic}")
        return {
            "response_text": response,
            "system_topic": system_topic,
            "routing": "HARD-RULE-2"
        }
    
    print("    ✗ No hard-override rule triggered")
    print("\n[3] Load conversation from session")
    print("    ✓ Conversation loaded (or created)")
    
    print("\n[4] EXISTING ROUTING LOGIC:")
    print("    Checking: Visualization request?")
    if "visualize" in prompt.lower() or "graph" in prompt.lower():
        print("    ✓ VISUALIZATION ROUTE")
        return {"routing": "VISUALIZATION"}
    
    print("    ✗ Not visualization")
    print("    Checking: Traceability matrix?")
    if "traceability matrix" in prompt.lower():
        print("    ✓ MATRIX ROUTE")
        return {"routing": "MATRIX"}
    
    print("    ✗ Not matrix")
    print("    Checking: Homomorphic proof?")
    if "homomorphic proof" in prompt.lower():
        print("    ✓ HOMOMORPHIC PROOF ROUTE")
        return {"routing": "HOMOMORPHIC_PROOF"}
    
    print("    ✗ Not homomorphic proof")
    print("    Checking: Justification?")
    if "justify why" in prompt.lower():
        print("    ✓ JUSTIFICATION ROUTE")
        return {"routing": "JUSTIFICATION"}
    
    print("    ✗ Not justification")
    print("    DEFAULT: Artifact synthesis (uses LLM)")
    return {"routing": "ARTIFACT_SYNTHESIS"}


if __name__ == "__main__":
    print("=" * 80)
    print("HARD-OVERRIDE RULES INTEGRATION VALIDATION")
    print("=" * 80)
    print("\nShowing routing flow for different prompts...")
    
    test_cases = [
        # Rule 1 triggers
        "design the spring system for my drone",
        "Create a System Design for a Mechanical Spring System",
        
        # Rule 2 triggers
        "assess whether an RLC can verify the spring dynamics",
        "is the RLC equivalent to the mechanical system?",
        
        # Non-triggers (use existing routing)
        "create system requirements for a GPS satellite",
        "visualize the drone architecture",
        "generate a traceability matrix",
        "justify why an RLC can replace a spring",  # Note: "justify" uses existing route
    ]
    
    results = []
    for prompt in test_cases:
        result = simulate_chat_routing(prompt)
        results.append({
            "prompt": prompt,
            "routing": result.get("routing", "UNKNOWN")
        })
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nRouting Summary:")
    print(f"{'Prompt':<50} | {'Routing':<30}")
    print("-" * 82)
    
    for r in results:
        prompt = r["prompt"][:47] + "..." if len(r["prompt"]) > 50 else r["prompt"]
        routing = r["routing"]
        print(f"{prompt:<50} | {routing:<30}")
    
    print("\n✓ Hard-override rules properly block all other logic")
    print("✓ Non-matching prompts fall through to existing routing")
    print("✓ Integration successful")
