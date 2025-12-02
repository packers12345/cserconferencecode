#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Systems_Engineering_Chatbot'))

from src.system_component_extractor import SystemComponentExtractor
from src.morphism_detector import MorphismDetector
from src.isomorphism_graph_renderer import IsomorphismGraphRenderer
from src.morphism_justification import JustificationGenerator
from src.api_integration import GeminiClient

def test_spring_circuit_visualization():
    print("Testing isomorphism visualization for: Mechanical Spring System <-> Electric Circuit Model\n")
    
    try:
        client = GeminiClient()
        
        print("Step 1: Extracting system specifications...")
        extractor = SystemComponentExtractor(client)
        
        system1_name = "mechanical spring system"
        system2_name = "electric circuit model"
        
        print(f"  Extracting {system1_name}...")
        system1_spec = extractor.extract_system_specification(system1_name)
        print(f"    - Input: {system1_spec.input.symbol}")
        print(f"    - Output: {system1_spec.output.symbol}")
        print(f"    - State vars: {system1_spec.state_variables.symbols}")
        
        print(f"  Extracting {system2_name}...")
        system2_spec = extractor.extract_system_specification(system2_name)
        print(f"    - Input: {system2_spec.input.symbol}")
        print(f"    - Output: {system2_spec.output.symbol}")
        print(f"    - State vars: {system2_spec.state_variables.symbols}")
        
        print("\nStep 2: Detecting morphisms...")
        detector = MorphismDetector(client)
        morphisms = detector.detect_morphisms(system1_spec, system2_spec)
        
        print(f"  Found {len(morphisms)} morphisms:")
        for m in morphisms:
            print(f"    - {m.id}: {m.morphism_type} (strength: {m.strength})")
            if isinstance(m.strength, str):
                print(f"      WARNING: Strength is string type: '{m.strength}'")
            else:
                print(f"      OK: Strength is {type(m.strength).__name__}: {m.strength}")
        
        print("\nStep 3: Rendering visualization...")
        renderer = IsomorphismGraphRenderer()
        svg_output = renderer.render_full_visualization(system1_spec, system2_spec, morphisms)
        
        if svg_output and '<svg' in svg_output:
            print("  ✓ SVG generated successfully")
            print(f"    - SVG length: {len(svg_output)} characters")
            
            if '<text' in svg_output:
                print("  ✓ Text elements present")
            if 'ISOMORPHIC' in svg_output or 'HOMOMORPHIC' in svg_output:
                print("  ✓ Morphism types rendered")
            if 'Avg Strength' in svg_output:
                print("  ✓ Statistics rendered")
        else:
            print("  ✗ SVG generation failed")
            return False
        
        print("\nStep 4: Generating justification...")
        justifier = JustificationGenerator(client)
        justification = justifier.generate_full_justification(system1_spec, system2_spec, morphisms)
        if justification:
            print(f"  ✓ Justification generated ({len(justification)} characters)")
        else:
            print("  ✗ Justification generation failed")
        
        print("\n✓ All tests passed!")
        
        print("\nSample visualization output (first 500 chars):")
        print(svg_output[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_spring_circuit_visualization()
    sys.exit(0 if success else 1)
