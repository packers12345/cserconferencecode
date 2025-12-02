#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Systems_Engineering_Chatbot'))

from src.isomorphism_graph_renderer import IsomorphismGraphRenderer
from src.morphism_detector import Morphism
from dataclasses import dataclass

@dataclass
class MockComponent:
    symbol: str
    description: str

@dataclass
class MockStateVariables:
    symbols: list
    descriptions: list
    dimension: int
    vector_form: str

@dataclass
class MockStateFunction:
    equations: str
    matrix_form: str
    A_matrix: str
    B_vector: str
    system_type: str

@dataclass
class MockTransferFunction:
    symbolic_form: str
    numerator: str
    denominator: str
    poles: str
    zeros: str
    order: int

@dataclass
class MockInterface:
    input_coupling: str
    output_measurement: str
    boundary_conditions: str
    energy_expression: str

@dataclass
class MockSystem:
    system_name: str
    input: MockComponent
    output: MockComponent
    state_variables: MockStateVariables
    next_state_function: MockStateFunction
    transfer_function: MockTransferFunction
    interface: MockInterface

def test_visualization_with_string_strength():
    print("Testing isomorphism graph rendering with string strength values...\n")
    
    try:
        renderer = IsomorphismGraphRenderer()
        
        system1 = MockSystem(
            system_name="Mechanical Spring System",
            input=MockComponent(symbol="F", description="Applied Force"),
            output=MockComponent(symbol="x", description="Displacement"),
            state_variables=MockStateVariables(
                symbols=["x", "v"],
                descriptions=["Position", "Velocity"],
                dimension=2,
                vector_form="[x, v]^T"
            ),
            next_state_function=MockStateFunction(
                equations="dx/dt = v, dv/dt = -kx/m - cv/m + F/m",
                matrix_form="[0 1; -k/m -c/m]",
                A_matrix="[0 1; -k/m -c/m]",
                B_vector="[0; 1/m]",
                system_type="Second-order linear"
            ),
            transfer_function=MockTransferFunction(
                symbolic_form="1/(ms^2 + cs + k)",
                numerator="1",
                denominator="ms^2 + cs + k",
                poles="-c/(2m) ± sqrt(c^2-4mk)/(2m)",
                zeros="none",
                order=2
            ),
            interface=MockInterface(
                input_coupling="Direct force application",
                output_measurement="Position sensor",
                boundary_conditions="Fixed support",
                energy_expression="(1/2)kx^2 + (1/2)mv^2"
            )
        )
        
        system2 = MockSystem(
            system_name="Electric Circuit Model",
            input=MockComponent(symbol="V", description="Input Voltage"),
            output=MockComponent(symbol="i", description="Current"),
            state_variables=MockStateVariables(
                symbols=["q", "i"],
                descriptions=["Charge", "Current"],
                dimension=2,
                vector_form="[q, i]^T"
            ),
            next_state_function=MockStateFunction(
                equations="dq/dt = i, di/dt = -q/LC - Ri/L + V/L",
                matrix_form="[0 1; -1/LC -R/L]",
                A_matrix="[0 1; -1/LC -R/L]",
                B_vector="[0; 1/L]",
                system_type="Second-order linear"
            ),
            transfer_function=MockTransferFunction(
                symbolic_form="1/(Ls^2 + Rs + 1/C)",
                numerator="1",
                denominator="Ls^2 + Rs + 1/C",
                poles="-R/(2L) ± sqrt(R^2-4L/C)/(2L)",
                zeros="none",
                order=2
            ),
            interface=MockInterface(
                input_coupling="Voltage source",
                output_measurement="Ammeter",
                boundary_conditions="Complete circuit",
                energy_expression="(1/2)Li^2 + (1/2)q^2/C"
            )
        )
        
        morphisms = [
            Morphism(
                id="M_Input",
                source="Input_S1",
                target="Input_S2",
                source_component="F",
                target_component="V",
                morphism_type="ISOMORPHIC",
                strength=0.95,
                justification="Both are energy inputs",
                analysis_points=["Analogous driving forces", "Similar input domains"],
                parameter_map={"F": "V"}
            ),
            Morphism(
                id="M_Input_String",
                source="Input_S1",
                target="Input_S2",
                source_component="F",
                target_component="V",
                morphism_type="ISOMORPHIC",
                strength="0.95",
                justification="String strength value test",
                analysis_points=["Test string conversion"],
                parameter_map={"F": "V"}
            ),
            Morphism(
                id="M_Output",
                source="Output_S1",
                target="Output_S2",
                source_component="x",
                target_component="i",
                morphism_type="HOMOMORPHIC",
                strength="0.85",
                justification="Both represent system response (string strength)",
                analysis_points=["Response magnitude mapping", "Different physical meaning"],
                parameter_map={"x": "i"}
            ),
            Morphism(
                id="M_State",
                source="State_S1",
                target="State_S2",
                source_component="[x,v]",
                target_component="[q,i]",
                morphism_type="ISOMORPHIC",
                strength=0.92,
                justification="State space isomorphism",
                analysis_points=["Same dimension", "Similar dynamics"],
                parameter_map={"x": "q", "v": "i"}
            ),
            Morphism(
                id="M_StateFn",
                source="StateTrans_S1",
                target="StateTrans_S2",
                source_component="State Transition Function",
                target_component="State Transition Function",
                morphism_type="HOMOMORPHIC",
                strength=0.88,
                justification="Similar matrix structure",
                analysis_points=["Second-order dynamics"],
                parameter_map={}
            ),
        ]
        
        print("Test Case 1: Mix of numeric and string strength values")
        print("=" * 70)
        for m in morphisms:
            strength_type = type(m.strength).__name__
            print(f"  {m.id}: strength={m.strength} (type={strength_type})")
        
        print("\nGenerating visualization...")
        svg_output = renderer.render_full_visualization(system1, system2, morphisms)
        
        if not svg_output:
            print("[FAIL] SVG output is empty")
            return False
        
        print("[PASS] SVG generated: {} characters".format(len(svg_output)))
        
        checks = [
            ('<svg', 'SVG root element'),
            ('Mechanical Spring System', 'System 1 name'),
            ('Electric Circuit Model', 'System 2 name'),
            ('ISOMORPHIC', 'Isomorphic type label'),
            ('HOMOMORPHIC', 'Homomorphic type label'),
            ('0.95', 'Numeric strength rendered'),
            ('Avg Strength:', 'Statistics section'),
            ('Total:', 'Morphism count'),
        ]
        
        print("\nValidation checks:")
        all_passed = True
        for check_str, description in checks:
            if check_str in svg_output:
                print("  [OK] {}: '{}' found".format(description, check_str))
            else:
                print("  [FAIL] {}: '{}' NOT found".format(description, check_str))
                all_passed = False
        
        if not all_passed:
            return False
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 70)
        
        print("\nSample SVG content verified:")
        print("-" * 70)
        print("  - Contains system names")
        print("  - Contains morphism types (ISOMORPHIC, HOMOMORPHIC)")
        print("  - Contains strength values")
        print("  - Statistics section rendered")
        
        return True
        
    except Exception as e:
        print("\n[FAIL] TEST FAILED:")
        print("  {}: {}".format(type(e).__name__, str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visualization_with_string_strength()
    sys.exit(0 if success else 1)
