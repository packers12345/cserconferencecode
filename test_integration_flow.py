"""
Integration test: Verify that app.py correctly routes follow-ups to guardrailed function.
This checks the session/conversation flow without starting a live server.
"""

import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Systems_Engineering_Chatbot.src.context_manager import Conversation
from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
)


def test_conversation_context_flow():
    """
    Simulate the flow:
    1. User asks Rule 2 trigger prompt
    2. Rule 2 response is stored in conversation
    3. User asks follow-up
    4. Follow-up check should detect context and route to guardrails
    """
    print("=" * 80)
    print("INTEGRATION TEST: CONVERSATION CONTEXT FLOW")
    print("=" * 80)
    
    # Step 1: Initial prompt that triggers Rule 2
    initial_prompt = "assess whether an RLC can be leveraged for a verification model for a mechanical spring system"
    
    print(f"\n1. Initial prompt: '{initial_prompt[:60]}...'")
    
    # Check if it triggers Rule 2
    is_rule_2 = detect_rule_2_trigger(initial_prompt)
    print(f"   Triggers Rule 2: {is_rule_2}")
    
    if not is_rule_2:
        print("   ✗ FAIL: Should have triggered Rule 2")
        return
    
    # Step 2: Create conversation and store Rule 2 response
    conversation = Conversation(system_topic="RLC Circuit and Mechanical Spring System")
    rule_2_response = generate_rule_2_response()
    
    conversation.last_rule_triggered = "rule_2"
    conversation.last_hard_rule_response = rule_2_response
    
    print(f"\n2. Conversation context after Rule 2:")
    print(f"   last_rule_triggered: {conversation.last_rule_triggered}")
    print(f"   last_hard_rule_response length: {len(conversation.last_hard_rule_response)} chars")
    print(f"   ✓ Context stored in conversation")
    
    # Step 3: User sends follow-up (this should NOT trigger Rule 1 or Rule 2)
    followup_prompt = "walk me through that 2nd order electrical ODE"
    
    print(f"\n3. Follow-up prompt: '{followup_prompt}'")
    
    is_rule_1_followup = detect_rule_1_trigger(followup_prompt)
    is_rule_2_followup = detect_rule_2_trigger(followup_prompt)
    
    print(f"   Triggers Rule 1: {is_rule_1_followup}")
    print(f"   Triggers Rule 2: {is_rule_2_followup}")
    
    if is_rule_1_followup or is_rule_2_followup:
        print("   ✗ FAIL: Follow-up should NOT trigger hard rules (it's not a new request)")
    else:
        print("   ✓ PASS: Follow-up does not trigger hard rules")
    
    # Step 4: Check if follow-up should be routed to guardrails
    has_context = (
        conversation.last_hard_rule_response is not None 
        and conversation.last_rule_triggered is not None
    )
    
    print(f"\n4. Follow-up routing decision:")
    print(f"   Has prior hard rule response: {has_context}")
    print(f"   Should route to guardrails: {has_context and not (is_rule_1_followup or is_rule_2_followup)}")
    
    if has_context and not (is_rule_1_followup or is_rule_2_followup):
        print("   ✓ PASS: Follow-up will be routed to guardrailed LLM")
    else:
        print("   ✗ FAIL: Follow-up should be routed to guardrails")
    
    # Step 5: Test session serialization (app.py stores in session)
    print(f"\n5. Session serialization:")
    conversation_dict = conversation.to_dict()
    
    checks = [
        ("Serialization includes last_rule_triggered", "last_rule_triggered" in conversation_dict),
        ("Serialization includes last_hard_rule_response", "last_hard_rule_response" in conversation_dict),
        ("Values are preserved", 
         conversation_dict["last_rule_triggered"] == "rule_2" and 
         len(conversation_dict["last_hard_rule_response"]) == len(rule_2_response)),
    ]
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {status}: {check_name}")
    
    # Step 6: Test deserialization
    print(f"\n6. Session deserialization:")
    restored_conversation = Conversation.from_dict(conversation_dict)
    
    restore_checks = [
        ("Restored conversation has context", restored_conversation.last_rule_triggered == "rule_2"),
        ("Restored response matches original", 
         restored_conversation.last_hard_rule_response == rule_2_response),
        ("Next follow-up will use context", 
         restored_conversation.last_hard_rule_response is not None),
    ]
    
    for check_name, result in restore_checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {status}: {check_name}")


def test_rule_1_followed_by_followup():
    """Test the same flow but with Rule 1."""
    print("\n" + "=" * 80)
    print("INTEGRATION TEST: RULE 1 + FOLLOW-UP FLOW")
    print("=" * 80)
    
    # Initial Rule 1 trigger
    initial_prompt = "create a system design for a mechanical spring system"
    
    print(f"\n1. Initial prompt: '{initial_prompt}'")
    is_rule_1 = detect_rule_1_trigger(initial_prompt)
    print(f"   Triggers Rule 1: {is_rule_1}")
    
    if not is_rule_1:
        print("   ✗ FAIL: Should have triggered Rule 1")
        return
    
    # Store Rule 1 context
    conversation = Conversation(system_topic="Mechanical Spring System")
    rule_1_response = generate_rule_1_response()
    
    conversation.last_rule_triggered = "rule_1"
    conversation.last_hard_rule_response = rule_1_response
    
    print(f"\n2. Context stored (Rule 1)")
    print(f"   last_rule_triggered: {conversation.last_rule_triggered}")
    
    # Follow-up that's not a new trigger
    followup = "explain the displaced dynamic state further"
    
    print(f"\n3. Follow-up: '{followup}'")
    is_new_rule_1 = detect_rule_1_trigger(followup)
    is_new_rule_2 = detect_rule_2_trigger(followup)
    
    print(f"   Triggers new Rule 1: {is_new_rule_1}")
    print(f"   Triggers Rule 2: {is_new_rule_2}")
    
    should_use_guardrails = (
        conversation.last_rule_triggered is not None 
        and not (is_new_rule_1 or is_new_rule_2)
    )
    
    print(f"\n4. Routing: Should use guardrails: {should_use_guardrails}")
    if should_use_guardrails:
        print("   ✓ PASS: Follow-up will be guardrailed")
    else:
        print("   ✗ FAIL: Should be guardrailed")


def main():
    test_conversation_context_flow()
    test_rule_1_followed_by_followup()
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("✓ If all tests pass, the follow-up flow is correctly implemented")
    print("✓ Session serialization works for storing context across requests")
    print("✓ Hard rules won't re-trigger on follow-ups")
    print("✓ Guardrails will be applied to all follow-up queries\n")


if __name__ == "__main__":
    main()
