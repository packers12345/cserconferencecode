import numpy as np
import sys
import os
from typing import Set, Dict, Tuple, Any

# Add the directory containing systems_mathematics.py to sys.path
# This assumes system_isomorphism_demo.py is in the same directory as systems_mathematics.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from systems_mathematics import SystemModel, State, Input, Output, InterfaceFunction, IsomorphismChecker

# --- 1. Define System Elements ---
# Mechanical Spring Elements
class MechanicalState(State): pass
class MechanicalInput(Input): pass
class MechanicalOutput(Output): pass
class MechanicalInterfaceFunction(InterfaceFunction): pass

# Electric Circuit Elements
class ElectricalState(State): pass
class ElectricalInput(Input): pass
class ElectricalOutput(Output): pass
class ElectricalInterfaceFunction(InterfaceFunction): pass

# --- 2. Define Dynamic Functions for Mechanical Spring (Mass-Spring-Damper) ---
def mechanical_transition_function(current_state: Tuple[float, float], applied_force: float, params: Dict[str, Any]) -> Tuple[float, float]:
    """
    Calculates the next state (position, velocity) for a mass-spring-damper system.
    current_state: (position, velocity)
    applied_force: F
    params: {'m': mass, 'k': spring_constant, 'c': damping_coefficient, 'dt': time_step}
    """
    x, v = current_state
    m = params['m']
    k = params['k']
    c = params['c']
    dt = params['dt']

    # Using Euler's method for simplicity in discrete time step
    # dx/dt = v
    # dv/dt = (F - kx - cv) / m
    
    new_v = v + dt * ((applied_force - k * x - c * v) / m)
    new_x = x + dt * v # Use current v for position update for simplicity
    
    return (new_x, new_v)

def mechanical_output_function(current_state: Tuple[float, float], applied_force: float, params: Dict[str, Any]) -> Tuple[float, float]:
    """
    Returns the observable outputs (position, velocity) for a mass-spring-damper system.
    """
    return current_state

# --- 3. Define Dynamic Functions for Electric Circuit (Series RLC) ---
def electrical_transition_function(current_state: Tuple[float, float], applied_voltage: float, params: Dict[str, Any]) -> Tuple[float, float]:
    """
    Calculates the next state (charge, current) for a series RLC circuit.
    current_state: (charge, current)
    applied_voltage: V
    params: {'L': inductance, 'R': resistance, 'C': capacitance, 'dt': time_step}
    """
    q, i = current_state
    L = params['L']
    R = params['R']
    C = params['C']
    dt = params['dt']

    # Using Euler's method for simplicity in discrete time step
    # dq/dt = i
    # di/dt = (V - Ri - q/C) / L
    
    new_i = i + dt * ((applied_voltage - R * i - q / C) / L)
    new_q = q + dt * i # Use current i for charge update for simplicity
    
    return (new_q, new_i)

def electrical_output_function(current_state: Tuple[float, float], applied_voltage: float, params: Dict[str, Any]) -> Tuple[float, float]:
    """
    Returns the observable outputs (charge, current) for a series RLC circuit.
    """
    return current_state

# --- 4. Instantiate System Models ---
# Mechanical Spring Model
mechanical_states = {MechanicalState('position'), MechanicalState('velocity')}
mechanical_inputs = {MechanicalInput('force')}
mechanical_outputs = {MechanicalOutput('position'), MechanicalOutput('velocity')}
mechanical_if_functions = {MechanicalInterfaceFunction('apply_force'), MechanicalInterfaceFunction('measure_position')}
mechanical_if_mapping = {MechanicalInput('force'): MechanicalInterfaceFunction('apply_force')}
mechanical_parameters = {'m': 1.0, 'k': 10.0, 'c': 0.5, 'dt': 0.01} # Example parameters

mechanical_spring_model = SystemModel(
    model_id="Mechanical_Spring_System",
    states=mechanical_states,
    inputs=mechanical_inputs,
    outputs=mechanical_outputs,
    transition_function=mechanical_transition_function,
    output_function=mechanical_output_function,
    interface_functions=mechanical_if_functions,
    if_mapping=mechanical_if_mapping,
    parameters=mechanical_parameters
)

# Electric Circuit Model
electrical_states = {ElectricalState('charge'), ElectricalState('current')}
electrical_inputs = {ElectricalInput('voltage')}
electrical_outputs = {ElectricalOutput('charge'), ElectricalOutput('current')}
electrical_if_functions = {ElectricalInterfaceFunction('apply_voltage'), ElectricalInterfaceFunction('measure_current')}
electrical_if_mapping = {ElectricalInput('voltage'): ElectricalInterfaceFunction('apply_voltage')}
electrical_parameters = {'L': 1.0, 'R': 0.5, 'C': 0.1, 'dt': 0.01} # Example parameters

electric_circuit_model = SystemModel(
    model_id="Electric_Circuit_System",
    states=electrical_states,
    inputs=electrical_inputs,
    outputs=electrical_outputs,
    transition_function=electrical_transition_function,
    output_function=electrical_output_function,
    interface_functions=electrical_if_functions,
    if_mapping=electrical_if_mapping,
    parameters=electrical_parameters
)

# --- 5. Define Isomorphic Mappings ---
# These mappings are based on the analogy:
# Mechanical: Force (F), Mass (m), Damping (c), Spring Constant (k), Position (x), Velocity (v)
# Electrical: Voltage (V), Inductance (L), Resistance (R), Inverse Capacitance (1/C), Charge (q), Current (i)

def state_map_mech_to_elec(mech_state_tuple: Tuple[float, float]) -> Tuple[float, float]:
    """Maps (position, velocity) to (charge, current)."""
    x, v = mech_state_tuple
    q = x  # Position maps to Charge
    i = v  # Velocity maps to Current
    return (q, i)

def input_map_mech_to_elec(mech_input_force: float) -> float:
    """Maps Force to Voltage."""
    F = mech_input_force
    V = F # Force maps to Voltage
    return V

def output_map_mech_to_elec(mech_output_tuple: Tuple[float, float]) -> Tuple[float, float]:
    """Maps (position, velocity) output to (charge, current) output."""
    x, v = mech_output_tuple
    q = x
    i = v
    return (q, i)

# Parameter mapping is handled implicitly by ensuring the numerical values align
# for the homomorphism check. For example, if m=1, L=1, then the mapping is 1:1.
# If k=10, 1/C=10 (so C=0.1), then the mapping is 1:1.
parameter_map_mech_to_elec = {
    'm': 'L',
    'c': 'R',
    'k': '1/C' # This is conceptual; actual values must be set in params
}

# --- 6. Demonstrate Isomorphism ---
if __name__ == "__main__":
    print("--- Demonstrating Isomorphism between Mechanical Spring and Electric Circuit ---")

    # Initialize IsomorphismChecker
    checker = IsomorphismChecker(mechanical_spring_model, electric_circuit_model)

    # Define test states and inputs (values for position/velocity and force)
    # These should be tuples representing (position, velocity) for states
    test_mechanical_states = {
        (0.0, 0.0),      # Initial rest state
        (0.1, 0.5),      # Some arbitrary state
        (-0.2, 0.1)
    }
    test_mechanical_inputs = {
        0.0,             # No force
        1.0,             # Positive force
        -0.5             # Negative force
    }

    # Perform the isomorphism check
    is_iso = checker.is_isomorphic(
        state_map=state_map_mech_to_elec,
        input_map=input_map_mech_to_elec,
        output_map=output_map_mech_to_elec,
        parameter_map=parameter_map_mech_to_elec, # This is conceptual for the checker
        test_states=test_mechanical_states,
        test_inputs=test_mechanical_inputs
    )

    if is_iso:
        print("\nConclusion: The Mechanical Spring System and Electric Circuit System are isomorphic under the defined mappings.")
        print("\n--- Justification using Wymorian System Theory ---")
        print("The demonstration above formally establishes an isomorphism (a bijective homomorphism) between the algebraic structures of the mechanical mass-spring-damper system and the electrical series RLC circuit.")
        print("According to Wymorian System Theory, the existence of such an isomorphism implies that these two systems are behaviorally equivalent. This means that despite their different physical realizations, they exhibit the same fundamental input-output behavior and internal state transitions when viewed through the lens of the defined mappings.")
        print("\nKey implications:")
        print("1.  **Interchangeability:** One system can be used as a direct model or analogue for the other. For example, an RLC circuit can be designed and analyzed to predict the dynamic response of a mechanical spring system, which can be advantageous for prototyping, cost-reduction, or safety reasons.")
        print("2.  **Preservation of Dynamics:** The homomorphic mappings ensure that the differential equations governing the behavior of one system are transformed into the differential equations governing the other. For instance, Newton's second law for the mechanical system maps directly to Kirchhoff's voltage law for the electrical system under the appropriate parameter and state transformations.")
        print("3.  **Degree of Homomorphism:** In this case, a full isomorphism represents the highest 'degree of homomorphism,' indicating a perfect structural and behavioral equivalence. This allows for a direct and reliable interchangeability between the models.")
        print("\nTherefore, the electric circuit model can effectively replace the mechanical spring model for analysis, simulation, and design, as their underlying system dynamics are structurally identical.")
    else:
        print("\nConclusion: The systems are NOT isomorphic under the defined mappings.")
