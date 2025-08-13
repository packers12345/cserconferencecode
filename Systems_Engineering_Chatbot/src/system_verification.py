import unittest
from systems_mathematics import (
    State, Input, Output, InterfaceFunction,
    SystemModel, SystemRequirement, SystemDesign,
    VerificationRequirement, VerificationMethod
)

class TestSystemMathematics(unittest.TestCase):

    def setUp(self):
        """Set up a common system model for testing."""
        # Define basic elements
        self.s1 = State("S1")
        self.s2 = State("S2")
        self.ix1 = Input("IoX1")
        self.ix2 = Input("IoX2")
        self.oy1 = Output("IoY1")
        self.oy2 = Output("IoY2")
        self.if1 = InterfaceFunction("IF1")

        # Define the functions for the model
        self.states = {self.s1, self.s2}
        self.inputs = {self.ix1, self.ix2}
        self.outputs = {self.oy1, self.oy2}
        self.transitions = {
            (self.s1, self.ix1): self.s1,
            (self.s1, self.ix2): self.s2,
            (self.s2, self.ix1): self.s1,
            (self.s2, self.ix2): self.s2,
        }
        self.output_function = {
            (self.s1, self.ix1): self.oy1,
            (self.s2, self.ix2): self.oy2,
        }
        self.interfaces = {self.if1}
        self.if_mapping = {
            self.ix1: self.if1,
            self.ix2: self.if1,
        }

        # Create a SystemDesign instance
        self.design = SystemDesign(
            design_id="DesignA",
            states=self.states,
            inputs=self.inputs,
            outputs=self.outputs,
            transition_function=self.transitions,
            output_function=self.output_function,
            interface_functions=self.interfaces,
            if_mapping=self.if_mapping
        )

    def test_system_requirement_pass(self):
        """Test an SR that the design satisfies."""
        # SR: The system must have at least two states.
        sr_predicate = lambda model: len(model.S) >= 2
        sr = SystemRequirement("SR_StateCount", sr_predicate)
        self.assertTrue(sr.check(self.design))

    def test_system_requirement_fail(self):
        """Test an SR that the design does not satisfy."""
        # SR: The system must have more than 5 inputs.
        sr_predicate = lambda model: len(model.X) > 5
        sr = SystemRequirement("SR_InputCount", sr_predicate)
        self.assertFalse(sr.check(self.design))

    def test_verification_requirement(self):
        """Test a VR on the system design."""
        # VR: Verify that input IoX2 always transitions to state S2.
        def vr_property(design):
            for (state, inp), next_state in design.N.items():
                if inp.id == "IoX2" and next_state.id != "S2":
                    return False
            return True
        
        vr = VerificationRequirement("VR_TransitionToS2", vr_property)
        self.assertTrue(vr.verify(self.design))

    def test_verification_method(self):
        """Test a VM that executes a verification test."""
        # VR: A simple property to test.
        vr_prop = lambda design: "IoX1" in [i.id for i in design.X]
        vr = VerificationRequirement("VR_InputExists", vr_prop)

        # VM: A test case with specific parameters.
        vm = VerificationMethod(
            vm_id="VM_Test1",
            parameterization={"TestParam": 123},
            target_vr=vr,
            related_design=self.design
        )
        # The VM's execute method should return the result of the VR check.
        self.assertTrue(vm.execute())

if __name__ == "__main__":
    unittest.main()
