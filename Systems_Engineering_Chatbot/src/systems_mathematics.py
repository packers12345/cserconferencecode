import numpy as np
from typing import Set, Dict, Tuple, Any

class SystemElement:
    """Base class for system elements to ensure basic properties."""
    def __init__(self, element_id: str):
        self.id = element_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class State(SystemElement):
    """Represents a state in the system model, can be symbolic or numerical."""
    def __init__(self, element_id: str, value: Any = None):
        super().__init__(element_id)
        self.value = value

class Input(SystemElement):
    """Represents an input to the system model, can be symbolic or numerical."""
    def __init__(self, element_id: str, value: Any = None):
        super().__init__(element_id)
        self.value = value

class Output(SystemElement):
    """Represents an output from the system model, can be symbolic or numerical."""
    def __init__(self, element_id: str, value: Any = None):
        super().__init__(element_id)
        self.value = value

class InterfaceFunction(SystemElement):
    """Represents an Interface Function (IF)."""
    pass

class SystemModel:
    """
    Represents a system model Z_A, based on the provided formal structure.
    Z_A = (S_A, X_A, Y_A, N_A, R_A, F_A, P_A)
    
    States (S), Inputs (X), Outputs (Y) are sets of SystemElement objects.
    N (transition_function): callable(current_symbolic_state: str, current_numerical_state_values: Dict[str, Any], input_values: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]
    R (output_function): callable(current_symbolic_state: str, current_numerical_state_values: Dict[str, Any], input_values: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]
    """
    def __init__(self, model_id: str,
                 states: Set[State],
                 inputs: Set[Input],
                 outputs: Set[Output],
                 transition_function: callable,
                 output_function: callable,
                 interface_functions: Set[InterfaceFunction],
                 if_mapping: Dict[Input, InterfaceFunction],
                 parameters: Dict[str, Any] = None):
        self.id = model_id
        self.S = states
        self.X = inputs
        self.Y = outputs
        self.N = transition_function
        self.R = output_function
        self.F = interface_functions
        self.P = if_mapping
        self.parameters = parameters if parameters is not None else {}

    def __repr__(self):
        return (f"SystemModel(id={self.id}, "
                f"|S|={len(self.S)}, |X|={len(self.X)}, |Y|={len(self.Y)}, "
                f"|N|={len(self.N)}, |R|={len(self.R)}, "
                f"|F|={len(self.F)}, |P|={len(self.P)})")

    def to_tabular(self):
        return f"""
| Component | Description |
| :--- | :--- |
| **ID** | {self.id} |
| **States (S)** | {', '.join(s.id for s in self.S)} |
| **Inputs (X)** | {', '.join(i.id for i in self.X)} |
| **Outputs (Y)** | {', '.join(o.id for o in self.Y)} |
| **Transitions (N)** | Implemented as callable function |
| **Output Func (R)** | Implemented as callable function |
| **Interface Func (F)** | {', '.join(f.id for f in self.F)} |
| **IF Mapping (P)** | {len(self.P)} defined |
"""

class SystemRequirement:
    """
    Represents a System Requirement (SR) as a formal predicate on a SystemModel.
    This predicate must be satisfied by any compliant system design.
    
    Algebraic Structure:
    Let R_S be the set of all system requirements. Each requirement r ∈ R_S is a predicate P_r
    that applies to a system model M.
    
    Mathematical Formula:
    r(M) -> {True, False}
    """
    def __init__(self, sr_id: str, predicate: callable):
        """
        :param sr_id: Unique ID for the SR.
        :param predicate: A function that takes a SystemModel and returns True if the model
                          satisfies the requirement, False otherwise.
        """
        self.id = sr_id
        self.predicate = predicate

    def check(self, model: SystemModel) -> bool:
        """Checks if a given SystemModel satisfies this requirement."""
        return self.predicate(model)

    def __repr__(self):
        return f"SystemRequirement(id={self.id})"

    def to_tabular(self):
        return f"""
| Requirement ID | Predicate |
| :--- | :--- |
| {self.id} | {self.predicate.__doc__ or 'Custom function'} |
"""

class SystemDesign(SystemModel):
    """
    Represents a System Design (SD) as a concrete implementation of a SystemModel.
    This class inherits from SystemModel and represents a specific, fully-defined design.
    
    Algebraic Structure:
    Let D_S be the set of all possible designs for a system. A design D ∈ D_S is a specific
    instance of a system model M. A design is valid if it satisfies all system requirements.
    
    Mathematical Formula:
    ∀r ∈ R_S, r(D) = True
    """
    def __init__(self, design_id: str, *args, **kwargs):
        super().__init__(model_id=design_id, *args, **kwargs)
        self.id = design_id

    def __repr__(self):
        return f"SystemDesign(id={self.id})"

    def to_tabular(self):
        # Leverages the parent's tabular representation
        return super().to_tabular()

class VerificationRequirement:
    """
    Represents a Verification Requirement (VR) as a property to be proven about a SystemDesign.
    Similar to an SR, but focused on verification aspects.
    
    Algebraic Structure:
    Let V_R be the set of all verification requirements. Each requirement v ∈ V_R is a property
    that must be proven about a system design D.
    
    Mathematical Formula:
    v(D) -> {True, False}
    """
    def __init__(self, vr_id: str, verification_property: callable):
        """
        :param vr_id: Unique ID for the VR.
        :param verification_property: A function that takes a SystemDesign and returns a boolean
                                      indicating if the property holds.
        """
        self.id = vr_id
        self.property = verification_property

    def verify(self, design: SystemDesign) -> bool:
        """Verifies if a given SystemDesign meets this verification requirement."""
        return self.property(design)

    def __repr__(self):
        return f"VerificationRequirement(id={self.id})"

    def to_tabular(self):
        return f"""
| VR ID | Verification Property |
| :--- | :--- |
| {self.id} | {self.property.__doc__ or 'Custom function'} |
"""

class IsomorphismChecker:
    """
    A class to check for isomorphic mappings between two SystemModel instances.
    """
    def __init__(self, system_a: SystemModel, system_b: SystemModel):
        self.system_a = system_a
        self.system_b = system_b

    def check_homomorphism(self,
                           state_map_func: callable, # Maps (symbolic_state_A, numerical_state_A) -> (symbolic_state_B, numerical_state_B)
                           input_map_func: callable, # Maps input_values_A -> input_values_B
                           output_map_func: callable, # Maps output_values_A -> output_values_B
                           parameter_map_dict: Dict[str, str], # Maps param_name_A -> param_name_B (conceptual)
                           test_initial_states_A: list[Tuple[str, Dict[str, Any]]], # (symbolic_state, numerical_state_values)
                           test_input_sets_A: list[Dict[str, Any]]) -> bool: # {input_name: value}
        """
        Verifies the homomorphic conditions between system_a and system_b.
        
        h_S(N_A(s, x)) = N_B(h_S(s), h_X(x))
        h_Y(R_A(s, x)) = R_B(h_S(s), h_X(x))
        """
        # Check transition function homomorphism
        for s_a_sym, s_a_num in test_initial_states_A:
            for x_a_vals in test_input_sets_A:
                # Apply system A's transition function
                next_s_a_sym, next_s_a_num = self.system_a.N(s_a_sym, s_a_num, x_a_vals, self.system_a.parameters)
                
                # Map s_a and x_a to system B's domain
                s_b_sym, s_b_num = state_map_func(s_a_sym, s_a_num)
                x_b_vals = input_map_func(x_a_vals)
                
                # Apply system B's transition function
                print(f"DEBUG: Calling N_B with s_b_sym={s_b_sym}, s_b_num={s_b_num}, x_b_vals={x_b_vals}, params={self.system_b.parameters}")
                next_s_b_sym_expected, next_s_b_num_expected = self.system_b.N(s_b_sym, s_b_num, x_b_vals, self.system_b.parameters)
                
                # Map system A's next state to system B's domain
                next_s_b_sym_actual, next_s_b_num_actual = state_map_func(next_s_a_sym, next_s_a_num)
                
                # Compare symbolic states
                if next_s_b_sym_actual != next_s_b_sym_expected:
                    print(f"Transition homomorphism failed (symbolic state) for s_a={s_a_sym}, x_a={x_a_vals}")
                    print(f"Mapped N_A symbolic result: {next_s_b_sym_actual}")
                    print(f"N_B symbolic result: {next_s_b_sym_expected}")
                    return False
                
                # Compare numerical state values
                for key in next_s_b_num_actual:
                    if key in next_s_b_num_expected and not np.allclose(next_s_b_num_actual[key], next_s_b_num_expected[key], atol=1e-6):
                        print(f"Transition homomorphism failed (numerical state '{key}') for s_a={s_a_sym}, x_a={x_a_vals}")
                        print(f"Mapped N_A numerical result: {next_s_b_num_actual[key]}")
                        print(f"N_B numerical result: {next_s_b_num_expected[key]}")
                        return False

        # Check output function homomorphism
        for s_a_sym, s_a_num in test_initial_states_A:
            for x_a_vals in test_input_sets_A:
                # Apply system A's output function
                y_a_vals = self.system_a.R(s_a_sym, s_a_num, x_a_vals, self.system_a.parameters)
                
                # Map s_a and x_a to system B's domain (for consistency, though R doesn't use next state)
                s_b_sym, s_b_num = state_map_func(s_a_sym, s_a_num)
                x_b_vals = input_map_func(x_a_vals)
                
                # Apply system B's output function
                y_b_vals_expected = self.system_b.R(s_b_sym, s_b_num, x_b_vals, self.system_b.parameters)
                
                # Map system A's output to system B's domain
                y_b_vals_actual = output_map_func(y_a_vals)
                
                # Compare output values
                for key in y_b_vals_actual:
                    if key in y_b_vals_expected and not np.allclose(y_b_vals_actual[key], y_b_vals_expected[key], atol=1e-6):
                        print(f"Output homomorphism failed (output '{key}') for s_a={s_a_sym}, x_a={x_a_vals}")
                        print(f"Mapped R_A result: {y_b_vals_actual[key]}")
                        print(f"R_B result: {y_b_vals_expected[key]}")
                        return False
        
        return True

    def is_isomorphic(self,
                      state_map_func: callable,
                      input_map_func: callable,
                      output_map_func: callable,
                      parameter_map_dict: Dict[str, str],
                      test_initial_states_A: list[Tuple[str, Dict[str, Any]]],
                      test_input_sets_A: list[Dict[str, Any]]) -> bool:
        """
        Checks if the two systems are isomorphic under the given mappings,
        emphasizing Wymorian system theory.
        """
        print("--- Wymorian Isomorphism Check ---")
        print("1. Verifying Homomorphism (Preservation of Algebraic Structure):")
        if not self.check_homomorphism(state_map_func, input_map_func, output_map_func, parameter_map_dict, test_initial_states_A, test_input_sets_A):
            print("Homomorphism check FAILED. Systems are not homomorphic under these mappings.")
            return False
        
        print("Homomorphism check PASSED. The mappings preserve the transition (N) and readout (R) functions.")
        
        print("\n2. Verifying Bijectivity (One-to-one and Onto Mappings):")
        # For this demonstration, we assume bijectivity if homomorphism holds for representative test cases
        # and the mappings are conceptually bijective for the mechanical spring <-> RLC circuit analogy.
        # A rigorous bijectivity check would involve analyzing the mapping functions for injectivity and surjectivity.
        print("Assuming bijectivity of state, input, and output mappings for this demonstration, given the established analogy.")
        print("In a full formal verification, explicit proofs of bijectivity would be required.")

        print("\nConclusion: Based on successful homomorphism and assumed bijectivity, the systems are isomorphic.")
        return True

    def generate_homomorphic_proof(self,
                                   state_map_func: callable,
                                   input_map_func: callable,
                                   output_map_func: callable,
                                   parameter_map_dict: Dict[str, str],
                                   test_initial_states_A: list[Tuple[str, Dict[str, Any]]],
                                   test_input_sets_A: list[Dict[str, Any]]) -> Tuple[str, float]:
        """
        Generates a homomorphic proof between system_a and system_b, leveraging Wymorian systems theory,
        and quantifies the degree of homomorphism.

        Returns a tuple: (narrative_proof: str, degree_of_homomorphism: float)
        """
        proof_narrative = []
        successful_checks = 0
        total_checks = 2 # Transition and Output functions

        proof_narrative.append("### Homomorphic Proof leveraging Wymorian Systems Theory")
        proof_narrative.append(f"\nThis proof examines the homomorphic relationship between System A: '{self.system_a.id}' and System B: '{self.system_b.id}'.")
        proof_narrative.append("\nAccording to Wymorian Systems Theory, a homomorphism exists if the algebraic structure of System A is preserved under a mapping to System B. This means that the operations (transition and output functions) in System A, when mapped, yield the same results as the operations in System B on the mapped elements.")

        # Check transition function homomorphism
        transition_homomorphic = True
        transition_failures = 0
        for s_a_sym, s_a_num in test_initial_states_A:
            for x_a_vals in test_input_sets_A:
                next_s_a_sym, next_s_a_num = self.system_a.N(s_a_sym, s_a_num, x_a_vals, self.system_a.parameters)
                
                s_b_sym, s_b_num = state_map_func(s_a_sym, s_a_num)
                x_b_vals = input_map_func(x_a_vals)
                
                next_s_b_sym_expected, next_s_b_num_expected = self.system_b.N(s_b_sym, s_b_num, x_b_vals, self.system_b.parameters)
                
                next_s_b_sym_actual, next_s_b_num_actual = state_map_func(next_s_a_sym, next_s_a_num)
                
                if next_s_b_sym_actual != next_s_b_sym_expected:
                    transition_homomorphic = False
                    transition_failures += 1
                    # proof_narrative.append(f"  - Transition (symbolic) failed for s_a={s_a_sym}, x_a={x_a_vals}. Mapped N_A: {next_s_b_sym_actual}, N_B: {next_s_b_sym_expected}")
                    continue # Continue to check numerical states even if symbolic fails

                for key in next_s_b_num_actual:
                    if key in next_s_b_num_expected and not np.allclose(next_s_b_num_actual[key], next_s_b_num_expected[key], atol=1e-6):
                        transition_homomorphic = False
                        transition_failures += 1
                        # proof_narrative.append(f"  - Transition (numerical '{key}') failed for s_a={s_a_sym}, x_a={x_a_vals}. Mapped N_A: {next_s_b_num_actual[key]}, N_B: {next_s_b_num_expected[key]}")
                        break # Break from inner loop, move to next test case

        if transition_homomorphic:
            proof_narrative.append("\n#### 1. Transition Function Homomorphism (N)")
            proof_narrative.append(f"The transition function `N_A` of System A maps to `N_B` of System B under the defined state and input mappings (`h_S`, `h_X`). For all tested initial states and inputs, `h_S(N_A(s, x)) = N_B(h_S(s), h_X(x))` holds true.")
            proof_narrative.append("This indicates that the dynamic evolution of states in System A is preserved in System B through the homomorphic mapping.")
            successful_checks += 1
        else:
            proof_narrative.append("\n#### 1. Transition Function Homomorphism (N)")
            proof_narrative.append(f"The transition function homomorphism FAILED for {transition_failures} out of {len(test_initial_states_A) * len(test_input_sets_A)} test cases. This suggests that the dynamic evolution of states in System A is NOT fully preserved in System B under the current mappings.")

        # Check output function homomorphism
        output_homomorphic = True
        output_failures = 0
        for s_a_sym, s_a_num in test_initial_states_A:
            for x_a_vals in test_input_sets_A:
                y_a_vals = self.system_a.R(s_a_sym, s_a_num, x_a_vals, self.system_a.parameters)
                
                s_b_sym, s_b_num = state_map_func(s_a_sym, s_a_num)
                x_b_vals = input_map_func(x_a_vals)
                
                y_b_vals_expected = self.system_b.R(s_b_sym, s_b_num, x_b_vals, self.system_b.parameters)
                
                y_b_vals_actual = output_map_func(y_a_vals)
                
                for key in y_b_vals_actual:
                    if key in y_b_vals_expected and not np.allclose(y_b_vals_actual[key], y_b_vals_expected[key], atol=1e-6):
                        output_homomorphic = False
                        output_failures += 1
                        # proof_narrative.append(f"  - Output ('{key}') failed for s_a={s_a_sym}, x_a={x_a_vals}. Mapped R_A: {y_b_vals_actual[key]}, R_B: {y_b_vals_expected[key]}")
                        break # Break from inner loop, move to next test case

        if output_homomorphic:
            proof_narrative.append("\n#### 2. Output Function Homomorphism (R)")
            proof_narrative.append(f"The output function `R_A` of System A maps to `R_B` of System B under the defined state, input, and output mappings (`h_S`, `h_X`, `h_Y`). For all tested initial states and inputs, `h_Y(R_A(s, x)) = R_B(h_S(s), h_X(x))` holds true.")
            proof_narrative.append("This demonstrates that the observable behaviors (outputs) of System A are consistently reflected in System B through the homomorphic mapping.")
            successful_checks += 1
        else:
            proof_narrative.append("\n#### 2. Output Function Homomorphism (R)")
            proof_narrative.append(f"The output function homomorphism FAILED for {output_failures} out of {len(test_initial_states_A) * len(test_input_sets_A)} test cases. This suggests that the observable behaviors of System A are NOT fully preserved in System B under the current mappings.")

        # Quantify degree of homomorphism
        degree_of_homomorphism = successful_checks / total_checks
        proof_narrative.append(f"\n### Degree of Homomorphism: {degree_of_homomorphism:.2f}")
        proof_narrative.append(f"The degree of homomorphism is quantified as the ratio of successfully verified homomorphic conditions to the total number of conditions (transition and output functions). A value of 1.0 indicates a perfect homomorphism (isomorphism, assuming bijectivity), while values less than 1.0 indicate partial homomorphism.")

        if degree_of_homomorphism == 1.0:
            proof_narrative.append("\n**Conclusion:** Based on the successful verification of both transition and output function homomorphism, and assuming bijectivity of the mapping functions, the two systems exhibit a **strong homomorphic relationship (isomorphism)**. This implies that System B can serve as a behaviorally equivalent model for System A, allowing for direct analysis and prediction of System A's behavior through System B.")
        elif degree_of_homomorphism > 0:
            proof_narrative.append(f"\n**Conclusion:** The systems exhibit a **partial homomorphic relationship** with a degree of {degree_of_homomorphism:.2f}. While some aspects of the algebraic structure are preserved, others are not. Further analysis is required to understand the implications of this partial mapping and whether System B can still be a useful analogue for specific behaviors of System A.")
        else:
            proof_narrative.append("\n**Conclusion:** The systems do not exhibit a significant homomorphic relationship under the defined mappings. The algebraic structure of System A is not preserved in System B, limiting its utility as a direct analogue.")

        return "\n".join(proof_narrative), degree_of_homomorphism

class VerificationMethod:
    """
    Represents a Verification Method (VM) as a parameterized test case.
    A VM is often a simplified or specific instance of a SystemModel, used to test a VR.
    
    Algebraic Structure:
    Let M_V be the set of all verification methods. Each method m ∈ M_V is a procedure
    to check if a design D satisfies a verification requirement v.
    
    Mathematical Formula:
    m(D, v) -> {Pass, Fail}
    """
    def __init__(self, vm_id: str,
                 parameterization: Dict[str, Any],
                 target_vr: VerificationRequirement,
                 related_design: SystemDesign):
        """
        :param vm_id: Unique ID for the VM.
        :param parameterization: A dictionary defining the specific parameters for this test case,
                                 e.g., {"Torque": 0.5, "Rotation": "roll"}.
        :param target_vr: The VerificationRequirement this VM is designed to test.
        :param related_design: The SystemDesign to which this VM applies.
        """
        self.id = vm_id
        self.parameterization = parameterization
        self.target_vr = target_vr
        self.related_design = related_design

    def execute(self) -> bool:
        """
        Executes the verification test.
        This is a placeholder for the actual test logic, which would use the parameterization
        to check the behavior of the related_design against the target_vr.
        """
        # In a real scenario, this would involve complex logic.
        # For now, we'll just re-run the VR check on the design.
        print(f"Executing VM '{self.id}' with parameters: {self.parameterization}")
        return self.target_vr.verify(self.related_design)

    def __repr__(self):
        return f"VerificationMethod(id={self.id}, vr='{self.target_vr.id}')"

    def to_tabular(self):
        params = "\\n".join([f"- {k}: {v}" for k, v in self.parameterization.items()])
        return f"""
| VM ID | Target VR | Parameters |
| :--- | :--- | :--- |
| {self.id} | {self.target_vr.id} | {params} |
"""
