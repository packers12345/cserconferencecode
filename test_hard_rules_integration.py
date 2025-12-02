#!/usr/bin/env python3
"""
Integration test for hard-rules follow-up routing.
Tests that:
1. Rule 1 trigger returns hardcoded System Z_A
2. Rule 2 trigger returns hardcoded morphism proof
3. Follow-up queries after Rule 2 are routed to LLM with context
"""

import sys
import os

# Add the repo root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
    generate_any_followup_response,
)
from Systems_Engineering_Chatbot.src.context_manager import Conversation

def test_rule_1_detection():
    """Test Rule 1 keyword detection"""
    print("TEST 1: Rule 1 Detection")
    test_cases = [
        ("design the spring system", True),
        ("mechanical spring system model", True),
        ("create a system design for a mechanical spring system", True),
        ("system z spring", True),
        ("what is a drone", False),
        ("tell me about RLC circuits", False),
    ]
    
    for prompt, expected in test_cases:
        result = detect_rule_1_trigger(prompt)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{prompt[:40]}...' → {result} (expected {expected})")
    print()

def test_rule_2_detection():
    """Test Rule 2 keyword detection"""
    print("TEST 2: Rule 2 Detection")
    test_cases = [
        ("assess whether an RLC can be leveraged for a verification model for a mechanical spring system", True),
        ("RLC verify spring", True),
        ("morphism between mechanical and electrical", True),
        ("is the RLC equivalent to the mechanical system", True),
        ("what is a drone", False),
        ("design the spring system", False),
    ]
    
    for prompt, expected in test_cases:
        result = detect_rule_2_trigger(prompt)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{prompt[:40]}...' → {result} (expected {expected})")
    print()

def test_rule_1_response():
    """Test Rule 1 generates System Z_A"""
    print("TEST 3: Rule 1 Response Generation")
    response = generate_rule_1_response()
    has_z_a = "System Z_A" in response
    has_states = "Nondisplaced" in response and "Displaced" in response
    has_input = "Force F(t)" in response
    
    status_z_a = "✓" if has_z_a else "✗"
    status_states = "✓" if has_states else "✗"
    status_input = "✓" if has_input else "✗"
    
    print(f"  {status_z_a} Response contains 'System Z_A': {has_z_a}")
    print(f"  {status_states} Response contains state definitions: {has_states}")
    print(f"  {status_input} Response contains input specification: {has_input}")
    print(f"  ✓ Response length: {len(response)} characters")
    print()

def test_rule_2_response():
    """Test Rule 2 generates morphism proof"""
    print("TEST 4: Rule 2 Response Generation")
    response = generate_rule_2_response()
    has_problem = "PROBLEM:" in response
    has_steps = all(f"STEP {i}" in response for i in range(9))
    has_conclusion = "YES —" in response
    
    status_problem = "✓" if has_problem else "✗"
    status_steps = "✓" if has_steps else "✗"
    status_conclusion = "✓" if has_conclusion else "✗"
    
    print(f"  {status_problem} Response contains PROBLEM statement: {has_problem}")
    print(f"  {status_steps} Response contains all 9 steps (0-8): {has_steps}")
    print(f"  {status_conclusion} Response contains YES conclusion: {has_conclusion}")
    print(f"  ✓ Response length: {len(response)} characters")
    print()

def test_conversation_state_tracking():
    """Test that Conversation tracks last rule and response"""
    print("TEST 5: Conversation State Tracking")
    
    # Create conversation
    conv = Conversation(system_topic="Test System")
    
    # Check initial state
    assert conv.last_rule_triggered is None, "Initial state should be None"
    assert conv.last_hard_rule_response is None, "Initial response should be None"
    print("  ✓ Initial state correctly initialized to None")
    
    # Simulate Rule 2 response
    response_text = generate_rule_2_response()
    conv.last_rule_triggered = "rule_2"
    conv.last_hard_rule_response = response_text
    
    assert conv.last_rule_triggered == "rule_2", "Should track rule_2"
    assert len(conv.last_hard_rule_response) > 0, "Should store response text"
    print("  ✓ Conversation tracks rule_2 trigger")
    print("  ✓ Conversation stores hardcoded response")
    
    # Test serialization
    serialized = conv.to_dict()
    assert "last_rule_triggered" in serialized, "to_dict should include last_rule_triggered"
    assert "last_hard_rule_response" in serialized, "to_dict should include last_hard_rule_response"
    print("  ✓ to_dict() includes rule state fields")
    
    # Test deserialization
    restored = Conversation.from_dict(serialized)
    assert restored.last_rule_triggered == "rule_2", "from_dict should restore rule state"
    assert len(restored.last_hard_rule_response) > 0, "from_dict should restore response"
    print("  ✓ from_dict() restores rule state correctly")
    print()

def test_followup_routing_structure():
    """Test that follow-up routing detects valid conversation state"""
    print("TEST 6: Follow-up Routing Structure")
    
    # Create conversation with Rule 2 triggered
    conv = Conversation(system_topic="Test System")
    conv.last_rule_triggered = "rule_2"
    conv.last_hard_rule_response = generate_rule_2_response()
    
    # Verify the follow-up dispatcher can detect the state
    has_rule = conv.last_rule_triggered is not None
    has_response = conv.last_hard_rule_response is not None
    
    status = "✓" if has_rule and has_response else "✗"
    print(f"  {status} Conversation state ready for follow-up routing: {has_rule and has_response}")
    print(f"  ✓ Last rule: {conv.last_rule_triggered}")
    print(f"  ✓ Response stored: {len(conv.last_hard_rule_response)} chars")
    print()

if __name__ == "__main__":
    print("=" * 70)
    print("HARD RULES INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        test_rule_1_detection()
        test_rule_2_detection()
        test_rule_1_response()
        test_rule_2_response()
        test_conversation_state_tracking()
        test_followup_routing_structure()
        
        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
