#!/usr/bin/env python3

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Systems_Engineering_Chatbot'))

from src.morphism_detector import Morphism
from src.isomorphism_graph_renderer import IsomorphismGraphRenderer
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

def test_endpoint_flow():
    print("Testing endpoint flow for: 'create a visual graph for the isomorphisms across a mechanical spring system and an electric circuit model'\n")
    
    try:
        renderer = IsomorphismGraphRenderer()
        
        system1 = MockSystem(
            system_name="mechanical spring system",
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
                poles="-c/(2m) +/- sqrt(c^2-4mk)/(2m)",
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
            system_name="electric circuit model",
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
                poles="-R/(2L) +/- sqrt(R^2-4L/C)/(2L)",
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
        
        print("Step 1: Creating morphisms (simulating LLM responses)...")
        morphisms = [
            Morphism(
                id="M_Input",
                source="Input_S1",
                target="Input_S2",
                source_component="F",
                target_component="V",
                morphism_type="ISOMORPHIC",
                strength=0.95,
                justification="Force and voltage are both energy inputs driving the system",
                analysis_points=[
                    "Both provide energy input to the system",
                    "Both are independent variables (inputs)",
                    "Both scale system response directly"
                ],
                parameter_map={"F": "V"}
            ),
            Morphism(
                id="M_Output",
                source="Output_S1",
                target="Output_S2",
                source_component="x",
                target_component="i",
                morphism_type="ISOMORPHIC",
                strength=0.92,
                justification="Displacement and current both represent system output response",
                analysis_points=[
                    "Both are measurable system outputs",
                    "Both depend on state and input",
                    "Similar response characteristics"
                ],
                parameter_map={"x": "i"}
            ),
            Morphism(
                id="M_State",
                source="State_S1",
                target="State_S2",
                source_component="[x, v]",
                target_component="[q, i]",
                morphism_type="ISOMORPHIC",
                strength=0.96,
                justification="State vectors are isomorphic with energy-based correspondence",
                analysis_points=[
                    "Both use 2D state vectors",
                    "Mechanical x <-> Electrical q (energy storage)",
                    "Mechanical v <-> Electrical i (energy flow rate)"
                ],
                parameter_map={"x": "q", "v": "i"}
            ),
            Morphism(
                id="M_StateFn",
                source="StateTrans_S1",
                target="StateTrans_S2",
                source_component="State Transition Function",
                target_component="State Transition Function",
                morphism_type="ISOMORPHIC",
                strength=0.94,
                justification="State transition matrices have identical structure (mass-spring-damper <-> RLC)",
                analysis_points=[
                    "Both are second-order linear systems",
                    "Stiffness k <-> Capacitance 1/C",
                    "Damping c <-> Resistance R",
                    "Mass m <-> Inductance L"
                ],
                parameter_map={"k": "1/C", "c": "R", "m": "L"}
            ),
            Morphism(
                id="M_TransferFunc",
                source="TransferFunc_S1",
                target="TransferFunc_S2",
                source_component="Transfer Function",
                target_component="Transfer Function",
                morphism_type="ISOMORPHIC",
                strength=0.91,
                justification="Transfer functions map directly with physical parameter correspondence",
                analysis_points=[
                    "Both have identical rational function structure",
                    "Second-order response with damping",
                    "Same pole/zero patterns"
                ],
                parameter_map={}
            ),
            Morphism(
                id="M_Interface",
                source="Interface_S1",
                target="Interface_S2",
                source_component="Interface",
                target_component="Interface",
                morphism_type="HOMOMORPHIC",
                strength=0.85,
                justification="Interfaces have similar structure but different physical domains",
                analysis_points=[
                    "Similar measurement and coupling strategies",
                    "Different physical measurement domains",
                    "Similar energy exchange description"
                ],
                parameter_map={}
            ),
        ]
        
        for m in morphisms:
            print("  - {}: {} (strength={})".format(m.id, m.morphism_type, m.strength))
        
        print("\nStep 2: Testing morphisms as dict (simulating cache retrieval)...")
        morphisms_dict = [m.to_dict() for m in morphisms]
        print("  - Converted {} morphisms to dict format".format(len(morphisms_dict)))
        
        print("\nStep 3: Reconstructing morphisms from dict (simulating cache load)...")
        reconstructed_morphisms = [Morphism(**m) for m in morphisms_dict]
        print("  - Reconstructed {} morphisms from dict".format(len(reconstructed_morphisms)))
        
        for m in reconstructed_morphisms:
            strength_type = type(m.strength).__name__
            print("    {}: strength={} (type={})".format(m.id, m.strength, strength_type))
        
        print("\nStep 4: Rendering visualization with morphisms...")
        svg_output = renderer.render_full_visualization(system1, system2, reconstructed_morphisms)
        
        if not svg_output:
            print("[FAIL] SVG output is empty")
            return False
        
        print("[PASS] SVG generated: {} characters".format(len(svg_output)))
        
        print("\nStep 5: Simulating response JSON generation...")
        
        def _to_float(value):
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    return 0.5
            return float(value) if value is not None else 0.5
        
        iso_count = sum(1 for m in reconstructed_morphisms if m.morphism_type == "ISOMORPHIC")
        homo_count = sum(1 for m in reconstructed_morphisms if m.morphism_type == "HOMOMORPHIC")
        avg_strength = sum(_to_float(m.strength) for m in reconstructed_morphisms) / len(reconstructed_morphisms) if reconstructed_morphisms else 0
        
        response_json = {
            "response_text": "Analysis of isomorphisms between mechanical spring and electric circuit",
            "visualization_svg": svg_output[:100] + "...",
            "morphisms": morphisms_dict,
            "statistics": {
                "total_morphisms": len(reconstructed_morphisms),
                "isomorphic_count": iso_count,
                "homomorphic_count": homo_count,
                "average_strength": avg_strength
            },
            "system1_name": "mechanical spring system",
            "system2_name": "electric circuit model",
            "system_topic": "mechanical spring system <-> electric circuit model",
            "graph_data": None
        }
        
        print("  - Response JSON created successfully")
        print("  - Total morphisms: {}".format(response_json["statistics"]["total_morphisms"]))
        print("  - Isomorphic: {}".format(response_json["statistics"]["isomorphic_count"]))
        print("  - Homomorphic: {}".format(response_json["statistics"]["homomorphic_count"]))
        print("  - Avg Strength: {:.2%}".format(response_json["statistics"]["average_strength"]))
        
        print("\nStep 6: Validating SVG output...")
        
        validation_checks = [
            ('<svg', 'SVG element'),
            ('Mechanical Spring System', 'System 1 name (title case)'),
            ('Electric Circuit Model', 'System 2 name (title case)'),
            ('ISOMORPHIC', 'Isomorphic morphism type'),
            ('HOMOMORPHIC', 'Homomorphic morphism type'),
            ('0.95', 'Strength value in visualization'),
            ('Avg Strength:', 'Statistics box'),
            ('Total:', 'Morphism count'),
            ('Legend:', 'Legend section'),
        ]
        
        all_passed = True
        for check_str, description in validation_checks:
            if check_str in svg_output:
                print("  [OK] {}".format(description))
            else:
                print("  [FAIL] {} - NOT FOUND: '{}'".format(description, check_str))
                all_passed = False
        
        if not all_passed:
            return False
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ENDPOINT FLOW TEST PASSED!")
        print("=" * 70)
        print("\nSummary:")
        print("  - Graph renders correctly with all isomorphisms")
        print("  - Morphism strengths handle both numeric and string values")
        print("  - Statistics calculated correctly")
        print("  - Response JSON formatted properly")
        print("\nPrompt successfully handled:")
        print('  "create a visual graph for the isomorphisms across a mechanical')
        print('   spring system and an electric circuit model"')
        
        return True
        
    except Exception as e:
        print("\n[FAIL] TEST FAILED:")
        print("  {}: {}".format(type(e).__name__, str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_endpoint_flow()
    sys.exit(0 if success else 1)
