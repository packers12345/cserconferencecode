"""
Test suite for hard_rules.py keyword detection and response generation.
Verifies that Rule 1 and Rule 2 are triggered correctly and produce expected outputs.
"""

import sys
import os

# Add the workspace to path
sys.path.insert(0, r'c:\Users\adiiy\OneDrive\Desktop\Code_Folder2')

from Systems_Engineering_Chatbot.src.hard_rules import (
    detect_rule_1_trigger,
    detect_rule_2_trigger,
    generate_rule_1_response,
    generate_rule_2_response,
)


def test_rule_1_detection():
    """Test Rule 1 keyword detection."""
    print("=" * 80)
    print("TEST: Rule 1 Detection (Spring System Design)")
    print("=" * 80)
    
    rule_1_triggers = [
        "create a system design for a mechanical spring system",
        "mechanical spring system model for the drone",
        "design the spring system for a suspension",
        "L1 model of spring dynamics",
        "system Z spring please",
        "spring system design requirements",
        "mechanical system abstraction example",
        "Create a System Design for a Mechanical Spring System",  # Case insensitive
    ]
    
    non_triggers = [
        "verify the RLC circuit",
        "design a system requirement",
        "assess the morphism between systems",
        "create a visualization",
    ]
    
    print("\nExpected triggers (should return True):")
    for trigger in rule_1_triggers:
        result = detect_rule_1_trigger(trigger)
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: '{trigger}'")
        assert result, f"Failed to detect Rule 1 trigger: {trigger}"
    
    print("\nExpected non-triggers (should return False):")
    for non_trigger in non_triggers:
        result = detect_rule_1_trigger(non_trigger)
        status = "✓ PASS" if not result else "✗ FAIL"
        print(f"  {status}: '{non_trigger}'")
        assert not result, f"False positive for Rule 1 trigger: {non_trigger}"
    
    print("\n✓ Rule 1 detection tests PASSED\n")


def test_rule_2_detection():
    """Test Rule 2 keyword detection."""
    print("=" * 80)
    print("TEST: Rule 2 Detection (RLC-Mechanical Morphism Verification)")
    print("=" * 80)
    
    rule_2_triggers = [
        "assess whether an RLC can verify spring dynamics",
        "RLC verify spring system",
        "RLC model spring system behavior",
        "mapping between RLC and spring",
        "morphism between mechanical and electrical systems",
        "structural equivalence RLC spring",
        "homomorphism mechanical electrical verification",
        "is the RLC equivalent to the mechanical system",
        "analog model spring system",
        "verification model RLC circuit for spring",
        "Assess Whether an RLC Can Verify",  # Case insensitive
    ]
    
    non_triggers = [
        "design a mechanical spring",
        "create system requirements",
        "generate a visualization",
        "trace the requirements",
    ]
    
    print("\nExpected triggers (should return True):")
    for trigger in rule_2_triggers:
        result = detect_rule_2_trigger(trigger)
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: '{trigger}'")
        assert result, f"Failed to detect Rule 2 trigger: {trigger}"
    
    print("\nExpected non-triggers (should return False):")
    for non_trigger in non_triggers:
        result = detect_rule_2_trigger(non_trigger)
        status = "✓ PASS" if not result else "✗ FAIL"
        print(f"  {status}: '{non_trigger}'")
        assert not result, f"False positive for Rule 2 trigger: {non_trigger}"
    
    print("\n✓ Rule 2 detection tests PASSED\n")


def test_rule_1_response():
    """Test Rule 1 response generation and guards."""
    print("=" * 80)
    print("TEST: Rule 1 Response Generation")
    print("=" * 80)
    
    response = generate_rule_1_response()
    
    # Check for required content markers
    required_markers = [
        "System Z_A (Mechanical Spring System):",
        "States:",
        "Nondisplaced",
        "Displaced (Static)",
        "Displaced (Dynamic)",
        "Input:",
        "Force F(t)",
        "Outputs:",
        "displacement x(t)",
        "velocity v(t) = dx/dt",
        "Next State Function:",
    ]
    
    print("\nChecking required content markers:")
    for marker in required_markers:
        if marker in response:
            print(f"  ✓ Found: '{marker}'")
        else:
            print(f"  ✗ MISSING: '{marker}'")
            assert False, f"Required marker missing: {marker}"
    
    # Check that Rule 2 content is NOT in Rule 1 response
    rule_2_markers = [
        "PROBLEM: Assess whether a series RLC circuit",
        "Characteristic equation: L r^2",
    ]
    
    print("\nChecking that Rule 2 content is NOT in Rule 1:")
    for marker in rule_2_markers:
        if marker not in response:
            print(f"  ✓ Correctly absent: '{marker}'")
        else:
            print(f"  ✗ VIOLATION: Rule 2 marker found in Rule 1: '{marker}'")
            assert False, f"Rule mixing detected: {marker}"
    
    # Check for absence of PSF/SR markers
    psr_markers = ["### SR-", "### SD-", "problem space", "solution space"]
    print("\nChecking for absence of PSF/SR markers:")
    for marker in psr_markers:
        if marker.lower() not in response.lower():
            print(f"  ✓ Correctly absent: '{marker}'")
        else:
            print(f"  ✗ VIOLATION: PSF/SR marker found: '{marker}'")
            assert False, f"PSF/SR injection detected: {marker}"
    
    print("\n✓ Rule 1 response generation tests PASSED\n")


def test_rule_2_response():
    """Test Rule 2 response generation and guards."""
    print("=" * 80)
    print("TEST: Rule 2 Response Generation")
    print("=" * 80)
    
    response = generate_rule_2_response()
    
    # Check for all 8 steps
    required_steps = [
        "STEP 0 —",
        "STEP 1 —",
        "STEP 2 —",
        "STEP 3 —",
        "STEP 4 —",
        "STEP 5 —",
        "STEP 6 —",
        "STEP 7 —",
        "STEP 8 —",
    ]
    
    print("\nChecking for all 8 steps:")
    for step in required_steps:
        if step in response:
            print(f"  ✓ Found: '{step}'")
        else:
            print(f"  ✗ MISSING: '{step}'")
            assert False, f"Missing step: {step}"
    
    # Check for required equations and concepts
    required_content = [
        "PROBLEM:",
        "2nd-order Mechanical ODE",
        "2nd-order Electrical ODE",
        "state-space form",
        "morphism φ",
        "damping ratio",
        "natural frequency",
        "YES — The RLC circuit can be used",
    ]
    
    print("\nChecking for required mathematical content:")
    for content in required_content:
        if content in response:
            print(f"  ✓ Found: '{content}'")
        else:
            print(f"  ✗ MISSING: '{content}'")
            assert False, f"Missing required content: {content}"
    
    # Check that Rule 1 content is NOT in Rule 2 response
    rule_1_markers = [
        "System Z_A (Mechanical Spring System):",
        "Nondisplaced",
        "Displaced (Static)",
    ]
    
    print("\nChecking that Rule 1 content is NOT in Rule 2:")
    for marker in rule_1_markers:
        if marker not in response:
            print(f"  ✓ Correctly absent: '{marker}'")
        else:
            print(f"  ✗ VIOLATION: Rule 1 marker found in Rule 2: '{marker}'")
            assert False, f"Rule mixing detected: {marker}"
    
    # Check for absence of PSF/SR markers
    psr_markers = ["### SR-", "### SD-", "### VR-", "problem space"]
    print("\nChecking for absence of PSF/SR markers:")
    for marker in psr_markers:
        if marker.lower() not in response.lower():
            print(f"  ✓ Correctly absent: '{marker}'")
        else:
            print(f"  ✗ VIOLATION: PSF/SR marker found: '{marker}'")
            assert False, f"PSF/SR injection detected: {marker}"
    
    print("\n✓ Rule 2 response generation tests PASSED\n")


def test_no_mutual_triggering():
    """Test that Rule 1 and Rule 2 triggers don't interfere."""
    print("=" * 80)
    print("TEST: No Mutual Triggering Between Rules")
    print("=" * 80)
    
    print("\nVerifying Rule 1 triggers don't match Rule 2:")
    rule_1_samples = [
        "create a system design for a mechanical spring system",
        "spring system design",
    ]
    for sample in rule_1_samples:
        if detect_rule_2_trigger(sample):
            print(f"  ✗ FAIL: Rule 1 sample triggered Rule 2: '{sample}'")
            assert False, f"Cross-trigger detected: {sample}"
        else:
            print(f"  ✓ PASS: '{sample}' correctly triggered only Rule 1")
    
    print("\nVerifying Rule 2 triggers don't match Rule 1:")
    rule_2_samples = [
        "assess whether an RLC can verify spring",
        "morphism between mechanical and electrical",
    ]
    for sample in rule_2_samples:
        if detect_rule_1_trigger(sample):
            print(f"  ✗ FAIL: Rule 2 sample triggered Rule 1: '{sample}'")
            assert False, f"Cross-trigger detected: {sample}"
        else:
            print(f"  ✓ PASS: '{sample}' correctly triggered only Rule 2")
    
    print("\n✓ No mutual triggering tests PASSED\n")


if __name__ == "__main__":
    try:
        test_rule_1_detection()
        test_rule_2_detection()
        test_rule_1_response()
        test_rule_2_response()
        test_no_mutual_triggering()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print("\nSummary:")
        print("- Rule 1 keyword detection: WORKING")
        print("- Rule 2 keyword detection: WORKING")
        print("- Rule 1 response generation: WORKING")
        print("- Rule 2 response generation: WORKING")
        print("- No response mixing: VERIFIED")
        print("- No PSF/SR injection: VERIFIED")
        print("- Guards and assertions: ENFORCED")
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print("TEST FAILED ✗")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print("TEST ERROR ✗")
        print("=" * 80)
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
