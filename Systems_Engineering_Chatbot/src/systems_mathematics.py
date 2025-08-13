import numpy as np
from typing import Set, Dict, Tuple, Any

class SystemElement:
    """Base class for system elements to ensure basic properties."""
    def __init__(self, element_id: str):
        self.id = element_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class State(SystemElement):
    """Represents a state in the system model."""
    pass

class Input(SystemElement):
    """Represents an input to the system model."""
    pass

class Output(SystemElement):
    """Represents an output from the system model."""
    pass

class InterfaceFunction(SystemElement):
    """Represents an Interface Function (IF)."""
    pass

class SystemModel:
    """
    Represents a system model Z_A, based on the provided formal structure.
    Z_A = (S_A, X_A, Y_A, N_A, R_A, F_A, P_A)
    """
    def __init__(self, model_id: str,
                 states: Set[State],
                 inputs: Set[Input],
                 outputs: Set[Output],
                 transition_function: Dict[Tuple[State, Input], State],
                 output_function: Dict[Tuple[State, Input], Output],
                 interface_functions: Set[InterfaceFunction],
                 if_mapping: Dict[Input, InterfaceFunction]):
        self.id = model_id
        self.S = states
        self.X = inputs
        self.Y = outputs
        self.N = transition_function
        self.R = output_function
        self.F = interface_functions
        self.P = if_mapping

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
| **Transitions (N)** | {len(self.N)} defined |
| **Output Func (R)** | {len(self.R)} defined |
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
