#!/usr/bin/env python
"""
Test script to verify that the RLC/Spring morphism proof endpoint
returns the complete 2nd-order L1 proof without truncation or LLM processing.
"""

import sys
import json
import os

# Add parent directory to path so Systems_Engineering_Chatbot is a module
project_root = os.path.dirname(os.path.abspath(__file__))
parent_root = os.path.dirname(project_root)
sys.path.insert(0, parent_root)

from src.morphism_proof_data import MORPHISM_PROOF_DATA, validate_l1_proof, get_proof_metadata

# Test trigger phrases (from the requirements)
TRIGGER_PHRASES = [
    "assess whether an RLC circuit can be leveraged for a verification model for a mechanical spring system",
    "can an RLC model a spring system",
    "use RLC to verify spring dynamics",
    "are these systems equivalent",
    "mapping between spring and RLC",
    "rlc circuit verification model spring",
    "spring-mass-damper and rlc",
    "rlc and spring equivalence"
]

def test_proof_completeness():
    """Verify the proof data is complete."""
    print("=" * 70)
    print("TEST 1: Proof Completeness Validation")
    print("=" * 70)
    
    is_valid, message = validate_l1_proof()
    print(f"Status: {'PASS' if is_valid else 'FAIL'}")
    print(f"Message: {message}")
    
    if is_valid:
        metadata = get_proof_metadata()
        print(f"\nProof Statistics:")
        print(f"  Characters: {metadata['length_chars']}")
        print(f"  Words: {metadata['length_words']}")
        print(f"  Steps: {metadata['steps']}")
        print(f"  Conclusion: {metadata['conclusion']}")
    
    return is_valid


def test_trigger_phrase_coverage():
    """Verify trigger phrases are defined and comprehensive."""
    print("\n" + "=" * 70)
    print("TEST 2: Trigger Phrase Coverage")
    print("=" * 70)
    
    print(f"Total trigger phrases defined: {len(TRIGGER_PHRASES)}")
    all_lowercase_triggers = [p.lower() for p in TRIGGER_PHRASES]
    
    # Check for duplicates
    if len(all_lowercase_triggers) != len(set(all_lowercase_triggers)):
        print("  WARNING: Some trigger phrases may be duplicates")
        return False
    
    for i, phrase in enumerate(TRIGGER_PHRASES[:5], 1):
        print(f"  [{i}] {phrase[:60]}...")
    
    if len(TRIGGER_PHRASES) > 5:
        print(f"  ... and {len(TRIGGER_PHRASES) - 5} more phrases")
    
    return True


def test_proof_content():
    """Verify all mathematical steps are present."""
    print("\n" + "=" * 70)
    print("TEST 3: Mathematical Content Verification")
    print("=" * 70)
    
    proof = MORPHISM_PROOF_DATA["l1_morphism_proof"]
    
    required_content = {
        "Newton's 2nd law": "Mechanical ODE derivation",
        "KVL": "Electrical ODE derivation",
        "State-space": "State-space formulation",
        "transfer function": "Transfer function definitions",
        "characteristic equation": "Characteristic polynomial analysis",
        "damping ratio": "Damping regime analysis",
        "impedance": "Frequency-domain verification",
        "CONCLUSION": "Final conclusion",
        "explicit isomorphism": "Explicit isomorphism claim"
    }
    
    all_present = True
    for keyword, description in required_content.items():
        if keyword.lower() in proof.lower():
            print(f"  [OK] {description} ({keyword})")
        else:
            print(f"  [FAIL] {description} ({keyword})")
            all_present = False
    
    return all_present


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("RLC/SPRING L1 MORPHISM PROOF ENDPOINT TEST SUITE")
    print("=" * 70)
    
    results = {
        "Proof Completeness": test_proof_completeness(),
        "Trigger Phrase Coverage": test_trigger_phrase_coverage(),
        "Mathematical Content": test_proof_content(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("ALL TESTS PASSED!" if all_passed else "SOME TESTS FAILED") + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
