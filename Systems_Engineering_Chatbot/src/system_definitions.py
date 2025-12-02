import numpy as np
from typing import Set, Dict, Tuple, Any
from Systems_Engineering_Chatbot.src.systems_mathematics import SystemModel, State, Input, Output, InterfaceFunction

# --- 1. Define System Elements for Mechanical Spring ---
class MechanicalState(State): pass
class MechanicalInput(Input): pass
class MechanicalOutput(Output): pass
class MechanicalInterfaceFunction(InterfaceFunction): pass

# --- 2. Define Dynamic Functions for Mechanical Spring (Z_SD1) ---
def mechanical_transition_function_sd1(current_symbolic_state: str,
                                       current_numerical_state_values: Dict[str, Any],
                                       input_values: Dict[str, Any],
                                       params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Next State Function (N) for the Mechanical Spring (Z_SD1).
    Dictates how the spring transitions from one state to another based on its current state and inputs.
    """
    x = current_numerical_state_values.get('displacement', 0.0)
    v = current_numerical_state_values.get('velocity', 0.0)
    applied_force_magnitude = input_values.get('x_applied_force_magnitude', 0.0)
    force_type = input_values.get('x_force_type', 'none') # 'compressive', 'tensile', 'none'
    initial_displacement = input_values.get('x_initial_displacement', 0.0)
    
    next_symbolic_state = current_symbolic_state
    next_numerical_state_values = current_numerical_state_values.copy()

    # n_1: ((s_equilibrium, x_applied_force_magnitude > 0, type_compressive), s_compressed)
    if current_symbolic_state == 's_equilibrium' and applied_force_magnitude > 0 and force_type == 'compressive':
        next_symbolic_state = 's_compressed'
        # Update numerical state based on force (simplified for symbolic transition)
        next_numerical_state_values['displacement'] = -applied_force_magnitude / params['k'] # F = -kx
        next_numerical_state_values['velocity'] = 0.0

    # n_2: ((s_equilibrium, x_applied_force_magnitude > 0, type_tensile), s_extended)
    elif current_symbolic_state == 's_equilibrium' and applied_force_magnitude > 0 and force_type == 'tensile':
        next_symbolic_state = 's_extended'
        next_numerical_state_values['displacement'] = applied_force_magnitude / params['k']
        next_numerical_state_values['velocity'] = 0.0

    # n_3: ((s_compressed, x_applied_force_magnitude = 0), s_oscillating)
    elif current_symbolic_state == 's_compressed' and applied_force_magnitude == 0:
        next_symbolic_state = 's_oscillating'
        # When released from compression, it starts oscillating.
        # Use continuous dynamics for one time step to get initial velocity.
        m = params['m']
        k = params['k']
        c = params['c']
        dt = params['dt']
        
        # Current state values
        x_current = current_numerical_state_values.get('displacement', 0.0)
        v_current = current_numerical_state_values.get('velocity', 0.0) # Should be 0.0 initially if held compressed
        
        # Calculate acceleration based on current displacement and velocity
        accel = (-k * x_current - c * v_current) / m
        
        # Update velocity and displacement for one time step
        new_v = v_current + dt * accel
        new_x = x_current + dt * v_current # Use current v for position update
        
        next_numerical_state_values['displacement'] = new_x
        next_numerical_state_values['velocity'] = new_v

    # n_4: ((s_extended, x_applied_force_magnitude = 0), s_oscillating)
    elif current_symbolic_state == 's_extended' and applied_force_magnitude == 0:
        next_symbolic_state = 's_oscillating'
        # When released from extension, it starts oscillating.
        # Use continuous dynamics for one time step to get initial velocity.
        m = params['m']
        k = params['k']
        c = params['c']
        dt = params['dt']
        
        # Current state values
        x_current = current_numerical_state_values.get('displacement', 0.0)
        v_current = current_numerical_state_values.get('velocity', 0.0) # Should be 0.0 initially if held extended
        
        # Calculate acceleration based on current displacement and velocity
        accel = (-k * x_current - c * v_current) / m
        
        # Update velocity and displacement for one time step
        new_v = v_current + dt * accel
        new_x = x_current + dt * v_current # Use current v for position update
        
        next_numerical_state_values['displacement'] = new_x
        next_numerical_state_values['velocity'] = new_v

    # n_5: ((s_oscillating, x_damping_effect_dominant), s_equilibrium)
    # This rule implies a decay over time. For a discrete step, we can model it as:
    elif current_symbolic_state == 's_oscillating':
        # Simplified damping effect: if velocity and displacement are near zero, return to equilibrium
        if abs(v) < params.get('damping_threshold_v', 0.01) and abs(x) < params.get('damping_threshold_x', 0.01):
            next_symbolic_state = 's_equilibrium'
            next_numerical_state_values['displacement'] = 0.0
            next_numerical_state_values['velocity'] = 0.0
        else: # If still oscillating, update numerical states based on continuous dynamics
            m = params['m']
            k = params['k']
            c = params['c']
            dt = params['dt']
            
            # Continuous dynamics for oscillating state (Euler's method)
            # dv/dt = (-kx - cv) / m
            # dx/dt = v
            
            accel = (-k * x - c * v) / m
            new_v = v + dt * accel
            new_x = x + dt * v # Use current v for position update
            
            next_numerical_state_values['displacement'] = new_x
            next_numerical_state_values['velocity'] = new_v

    return (next_symbolic_state, next_numerical_state_values)

def mechanical_output_function_sd1(current_symbolic_state: str,
                                   current_numerical_state_values: Dict[str, Any],
                                   input_values: Dict[str, Any],
                                   params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Readout Function (R) for the Mechanical Spring (Z_SD1).
    Maps internal states and inputs to observable outputs.
    """
    x = current_numerical_state_values.get('displacement', 0.0)
    v = current_numerical_state_values.get('velocity', 0.0)
    k = params['k']
    m = params['m']
    
    outputs = {}

    # r_1: (s_compressed, x_current_displacement) -> y_reaction_force_compressive
    # r_2: (s_extended, x_current_displacement) -> y_reaction_force_tensile
    if current_symbolic_state in ['s_compressed', 's_extended', 's_oscillating']:
        outputs['y_reaction_force'] = -k * x # Hooke's Law
        outputs['y_current_displacement'] = x
        outputs['y_stored_potential_energy'] = 0.5 * k * x**2

    # r_4: (s_oscillating, x_spring_constant, x_effective_mass) -> y_oscillation_frequency
    if current_symbolic_state == 's_oscillating' and m > 0 and k > 0:
        outputs['y_oscillation_frequency'] = np.sqrt(k / m) / (2 * np.pi) # Undamped natural frequency

    return outputs

# --- 3. Instantiate Mechanical Spring System Model (Z_SD1) ---
mechanical_states_set = {
    MechanicalState('s_equilibrium'),
    MechanicalState('s_compressed'),
    MechanicalState('s_extended'),
    MechanicalState('s_oscillating')
}
mechanical_inputs_set = {
    MechanicalInput('x_applied_force_magnitude'),
    MechanicalInput('x_initial_displacement'),
    MechanicalInput('x_environmental_temperature'), # Not used in dynamics, but part of definition
    MechanicalInput('x_force_type') # Added for clarity in transition rules
}
mechanical_outputs_set = {
    MechanicalOutput('y_reaction_force'),
    MechanicalOutput('y_current_displacement'),
    MechanicalOutput('y_stored_potential_energy'),
    MechanicalOutput('y_oscillation_frequency')
}
mechanical_if_functions_set = {
    MechanicalInterfaceFunction('apply_force'),
    MechanicalInterfaceFunction('measure_displacement'),
    MechanicalInterfaceFunction('measure_velocity')
}
mechanical_if_mapping_dict = {
    MechanicalInput('x_applied_force_magnitude'): MechanicalInterfaceFunction('apply_force')
}
mechanical_parameters_dict = {
    'm': 1.0, # mass
    'k': 10.0, # spring constant
    'c': 0.5, # damping coefficient
    'dt': 0.01, # time step for numerical integration
    'damping_threshold_v': 0.01, # velocity threshold for equilibrium
    'damping_threshold_x': 0.01  # displacement threshold for equilibrium
}

mechanical_spring_sd1 = SystemModel(
    model_id="Z_SD1_Mechanical_Spring",
    states=mechanical_states_set,
    inputs=mechanical_inputs_set,
    outputs=mechanical_outputs_set,
    transition_function=mechanical_transition_function_sd1,
    output_function=mechanical_output_function_sd1,
    interface_functions=mechanical_if_functions_set,
    if_mapping=mechanical_if_mapping_dict,
    parameters=mechanical_parameters_dict
)

# --- 4. Define System Elements for Electric Circuit ---
class ElectricalState(State): pass
class ElectricalInput(Input): pass
class ElectricalOutput(Output): pass
class ElectricalInterfaceFunction(InterfaceFunction): pass

# --- 5. Define Dynamic Functions for Electric Circuit (VM1) ---
def electrical_transition_function_vm1(current_symbolic_state: str,
                                       current_numerical_state_values: Dict[str, Any],
                                       input_values: Dict[str, Any],
                                       params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Next State Function (N) for the Electric Circuit (VM1 - Series RLC).
    Models the behavior of a series RLC circuit.
    States: charge (q), current (i)
    Input: applied_voltage (V)
    """
    q = current_numerical_state_values.get('charge', 0.0)
    i = current_numerical_state_values.get('current', 0.0)
    applied_voltage = input_values.get('x_electrical_excitation', 0.0)
    
    L = params['L']
    R = params['R']
    C = params['C']
    dt = params['dt']

    next_numerical_state_values = current_numerical_state_values.copy()
    next_symbolic_state = current_symbolic_state

    # If an external voltage is applied, the capacitor will charge/discharge.
    # For the initial step of homomorphism, we need to ensure the immediate effect
    # of applied voltage on charge is analogous to force on displacement.
    if applied_voltage != 0.0:
        # Analogous to mechanical: x = F/k
        # Electrical: q = V * C (steady state charge on capacitor if R=0, L=0, or initial response)
        # For the purpose of matching the mechanical system's immediate displacement,
        # we set the charge directly based on the applied voltage and capacitance.
        next_numerical_state_values['charge'] = applied_voltage * C
        next_numerical_state_values['current'] = 0.0 # Assume initial current is zero upon voltage application
        next_symbolic_state = 's_charged'
    else:
        # If no applied voltage, proceed with dynamic integration (Euler's method)
        # dq/dt = i
        # di/dt = (V - Ri - q/C) / L
        
        di_dt = (applied_voltage - R * i - q / C) / L
        
        new_i = i + dt * di_dt
        new_q = q + dt * i
        
        next_numerical_state_values['charge'] = new_q
        next_numerical_state_values['current'] = new_i

        # Refined symbolic state transitions for RLC to align with mechanical analogy
        if abs(new_i) > params.get('oscillation_threshold_i', 0.01) or abs(new_q) > params.get('oscillation_threshold_q', 0.01):
            next_symbolic_state = 's_oscillating_elec'
        else:
            next_symbolic_state = 's_equilibrium_elec'

    return (next_symbolic_state, next_numerical_state_values)

def electrical_output_function_vm1(current_symbolic_state: str,
                                   current_numerical_state_values: Dict[str, Any],
                                   input_values: Dict[str, Any],
                                   params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Readout Function (R) for the Electric Circuit (VM1).
    Maps internal states and inputs to observable outputs.
    """
    q = current_numerical_state_values.get('charge', 0.0)
    i = current_numerical_state_values.get('current', 0.0)
    L = params['L']
    C = params['C']
    
    outputs = {}
    outputs['y_electrical_charge'] = q
    outputs['y_electrical_current'] = i
    outputs['y_voltage_capacitor'] = q / C
    outputs['y_voltage_inductor'] = L * ( (input_values.get('x_electrical_excitation', 0.0) - params['R'] * i - q / C) / L ) # L * di/dt
    
    if L > 0 and C > 0:
        outputs['y_electrical_oscillation_frequency'] = 1 / (2 * np.pi * np.sqrt(L * C)) # Undamped natural frequency

    return outputs

# --- 6. Instantiate Electric Circuit System Model (VM1) ---
electrical_states_set = {
    ElectricalState('s_equilibrium_elec'),
    ElectricalState('s_charged'), # Analogous to compressed/extended
    ElectricalState('s_oscillating_elec')
}
electrical_inputs_set = {
    ElectricalInput('x_electrical_excitation')
}
electrical_outputs_set = {
    ElectricalOutput('y_electrical_charge'),
    ElectricalOutput('y_electrical_current'),
    ElectricalOutput('y_voltage_capacitor'),
    ElectricalOutput('y_voltage_inductor'),
    ElectricalOutput('y_electrical_oscillation_frequency')
}
electrical_if_functions_set = {
    ElectricalInterfaceFunction('apply_voltage'),
    ElectricalInterfaceFunction('measure_charge'),
    ElectricalInterfaceFunction('measure_current')
}
electrical_if_mapping_dict = {
    ElectricalInput('x_electrical_excitation'): ElectricalInterfaceFunction('apply_voltage')
}
electrical_parameters_dict = {
    'L': 1.0, # inductance (analogous to mass m)
    'R': 0.5, # resistance (analogous to damping c)
    'C': 0.1, # capacitance (analogous to 1/k, so k=1/C)
    'dt': 0.01, # time step
    'oscillation_threshold_i': 0.01,
    'oscillation_threshold_q': 0.01
}

electric_circuit_vm1 = SystemModel(
    model_id="VM1_Electric_Circuit",
    states=electrical_states_set,
    inputs=electrical_inputs_set,
    outputs=electrical_outputs_set,
    transition_function=electrical_transition_function_vm1,
    output_function=electrical_output_function_vm1,
    interface_functions=electrical_if_functions_set,
    if_mapping=electrical_if_mapping_dict,
    parameters=electrical_parameters_dict
)
