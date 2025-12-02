"""
Test script to validate hard-override rules and follow-up query support.
Tests both Rule 1 (Spring System Z_A) and Rule 2 (RLC Morphism Proof) with follow-up detection.
"""

import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
)
from Systems_Engineering_Chatbot.src.context_manager import Conversation


def test_rule_1_trigger():
    """Test Rule 1 trigger detection."""
    print("\n=== TEST: Rule 1 Trigger Detection ===")
    
    test_cases = [
        ("design the spring system", True),
        ("mechanical spring system model", True),
        ("create a system design for a mechanical spring system", True),
        ("system Z spring", True),
        ("L1 model of spring", True),
        ("show me a drone system", False),
        ("what is an RLC circuit", False),
    ]
    
    for prompt, expected in test_cases:
        result = detect_rule_1_trigger(prompt)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: '{prompt}' → {result} (expected {expected})")


def test_rule_2_trigger():
    """Test Rule 2 trigger detection."""
    print("\n=== TEST: Rule 2 Trigger Detection ===")
    
    test_cases = [
        ("assess whether an RLC can be leveraged", True),
        ("RLC verify spring", True),
        ("morphism between mechanical and electrical", True),
        ("is the RLC equivalent to the mechanical system", True),
        ("mapping between RLC and spring", True),
        ("design a spring system", False),
        ("what is a drone", False),
    ]
    
    for prompt, expected in test_cases:
        result = detect_rule_2_trigger(prompt)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: '{prompt}' → {result} (expected {expected})")


def test_rule_1_response_structure():
    """Test that Rule 1 response has correct structure."""
    print("\n=== TEST: Rule 1 Response Structure ===")
    
    response = generate_rule_1_response()
    
    # Check for key markers
    checks = [
        ("Contains 'System Z_A'", "System Z_A" in response),
        ("Contains 'States'", "States:" in response),
        ("Contains 'Nondisplaced'", "Nondisplaced" in response),
        ("Contains 'Displaced (Static)'", "Displaced (Static)" in response),
        ("Contains 'Displaced (Dynamic)'", "Displaced (Dynamic)" in response),
        ("Contains 'Force F(t)'", "Force F(t)" in response),
        ("Contains displacement and velocity outputs", "displacement x(t)" in response and "velocity v(t)" in response),
        ("Does NOT contain RLC markers", "RLC circuit" not in response and "KVL" not in response),
    ]
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")


def test_rule_2_response_structure():
    """Test that Rule 2 response has correct structure."""
    print("\n=== TEST: Rule 2 Response Structure ===")
    
    response = generate_rule_2_response()
    
    # Check for key markers and steps
    checks = [
        ("Contains PROBLEM statement", "PROBLEM:" in response),
        ("Contains STEP 0", "STEP 0" in response),
        ("Contains STEP 1", "STEP 1" in response),
        ("Contains STEP 8", "STEP 8" in response),
        ("Contains mechanical ODE", "m x''(t) + c x'(t) + k x(t) = F(t)" in response),
        ("Contains electrical ODE", "L q''(t) + R q'(t) + (1/C) q(t) = E(t)" in response),
        ("Contains morphism mapping", "x ↔ q" in response),
        ("Contains YES conclusion", "YES — The RLC circuit can be used" in response),
        ("Does NOT contain spring system states", "Nondisplaced" not in response),
    ]
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")


def test_conversation_context_tracking():
    """Test that Conversation class tracks rule context."""
    print("\n=== TEST: Conversation Context Tracking ===")
    
    conversation = Conversation(system_topic="Test System")
    
    # Test initial state
    checks = [
        ("last_rule_triggered is None initially", conversation.last_rule_triggered is None),
        ("last_hard_rule_response is None initially", conversation.last_hard_rule_response is None),
    ]
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    # Test setting rule state
    conversation.last_rule_triggered = "rule_1"
    conversation.last_hard_rule_response = "System Z_A response"
    
    # Test serialization and deserialization
    data = conversation.to_dict()
    restored_conversation = Conversation.from_dict(data)
    
    checks = [
        ("Serialization includes last_rule_triggered", "last_rule_triggered" in data),
        ("Serialization includes last_hard_rule_response", "last_hard_rule_response" in data),
        ("Deserialized last_rule_triggered is 'rule_1'", restored_conversation.last_rule_triggered == "rule_1"),
        ("Deserialized last_hard_rule_response matches", restored_conversation.last_hard_rule_response == "System Z_A response"),
    ]
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")


def main():
    """Run all tests."""
    print("=" * 70)
    print("TESTING HARD-OVERRIDE RULES")
    print("=" * 70)
    
    test_rule_1_trigger()
    test_rule_2_trigger()
    test_rule_1_response_structure()
    test_rule_2_response_structure()
    test_conversation_context_tracking()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
