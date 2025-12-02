import json
from typing import List, Dict, Any, Any
from dataclasses import dataclass


def _safe_float_conversion(value: Any, default: float = 0.5) -> float:
    """Safely converts a value to float, handling strings like 'strong' or None."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            # Handle qualitative strings if necessary, or just return default
            if value.lower() == 'strong': return 0.9
            if value.lower() == 'medium': return 0.7
            if value.lower() == 'weak': return 0.3
            return default
    return default


@dataclass
class Morphism:
    id: str
    source: str
    target: str
    source_component: str
    target_component: str
    morphism_type: str
    strength: float
    justification: str
    analysis_points: List[str]
    parameter_map: Dict[str, str]
    transformation: str = ""
    detailed_justification: str = ""
    information_loss: str = ""
    physical_meaning: Dict = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'source_component': self.source_component,
            'target_component': self.target_component,
            'morphism_type': self.morphism_type,
            'strength': self.strength,
            'justification': self.justification,
            'analysis_points': self.analysis_points,
            'parameter_map': self.parameter_map,
            'transformation': self.transformation,
            'detailed_justification': self.detailed_justification,
            'information_loss': self.information_loss,
            'physical_meaning': self.physical_meaning or {}
        }


class MorphismDetector:
    def __init__(self, llm_client):
        self.llm = llm_client

    def detect_morphisms(self, system1, system2) -> List[Morphism]:
        morphisms = []

        morphisms.append(self.analyze_input_morphism(system1, system2))
        morphisms.append(self.analyze_output_morphism(system1, system2))
        morphisms.append(self.analyze_state_morphism(system1, system2))
        morphisms.append(self.analyze_state_transition_morphism(system1, system2))

        if system1.transfer_function and system2.transfer_function:
            morphisms.append(self.analyze_transfer_function_morphism(system1, system2))

        morphisms.append(self.analyze_interface_morphism(system1, system2))

        return morphisms

    def analyze_input_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare these two system inputs and determine their morphism relationship:

INPUT 1:
- Symbol: {system1.input.symbol}
- Description: {system1.input.description}
- Domain: {system1.input.domain}
- Units: {system1.input.units}
- Definition: {system1.input.equation}

INPUT 2:
- Symbol: {system2.input.symbol}
- Description: {system2.input.description}
- Domain: {system2.input.domain}
- Units: {system2.input.units}
- Definition: {system2.input.equation}

Provide analysis as JSON:
{{
    "morphism_type": "ISOMORPHIC|HOMOMORPHIC|PARTIAL|NONE",
    "strength": 0.0 to 1.0,
    "justification": "One sentence explanation",
    "analysis_points": [
        "Point 1",
        "Point 2"
    ],
    "parameter_correspondence": {{}},
    "transformation_equation": "Any transformation needed"
}}

Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'PARTIAL',
                'strength': 0.5,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_Input",
            source="Input_S1",
            target="Input_S2",
            source_component=system1.input.symbol,
            target_component=system2.input.symbol,
            morphism_type=response.get('morphism_type', 'PARTIAL'),
            strength=_safe_float_conversion(response.get('strength', 0.5)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', '')
        )

    def analyze_output_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare these two system outputs and determine their morphism relationship:

OUTPUT 1:
- Symbol: {system1.output.symbol}
- Description: {system1.output.description}
- Domain: {system1.output.domain}
- Units: {system1.output.units}
- Definition: {system1.output.equation}

OUTPUT 2:
- Symbol: {system2.output.symbol}
- Description: {system2.output.description}
- Domain: {system2.output.domain}
- Units: {system2.output.units}
- Definition: {system2.output.equation}

Provide analysis as JSON (morphism_type, strength 0-1, justification, analysis_points, parameter_correspondence, transformation_equation).
Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'PARTIAL',
                'strength': 0.5,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_Output",
            source="Output_S1",
            target="Output_S2",
            source_component=system1.output.symbol,
            target_component=system2.output.symbol,
            morphism_type=response.get('morphism_type', 'PARTIAL'),
            strength=_safe_float_conversion(response.get('strength', 0.5)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', '')
        )

    def analyze_state_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare these two state vector specifications and determine morphism:

STATE 1:
- Symbols: {system1.state_variables.symbols}
- Descriptions: {system1.state_variables.descriptions}
- Dimension: {system1.state_variables.dimension}
- Vector form: {system1.state_variables.vector_form}

STATE 2:
- Symbols: {system2.state_variables.symbols}
- Descriptions: {system2.state_variables.descriptions}
- Dimension: {system2.state_variables.dimension}
- Vector form: {system2.state_variables.vector_form}

Provide JSON: morphism_type, strength, justification, analysis_points, parameter_correspondence, transformation_equation.
Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'PARTIAL',
                'strength': 0.5,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_State",
            source="State_S1",
            target="State_S2",
            source_component=str(system1.state_variables.symbols),
            target_component=str(system2.state_variables.symbols),
            morphism_type=response.get('morphism_type', 'PARTIAL'),
            strength=_safe_float_conversion(response.get('strength', 0.5)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', '')
        )

    def analyze_state_transition_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare these state transition functions for morphism:

SYSTEM 1 STATE FUNCTION:
Equations: {system1.next_state_function.equations}
Matrix form: {system1.next_state_function.matrix_form}
A matrix: {system1.next_state_function.A_matrix}
B vector: {system1.next_state_function.B_vector}
Type: {system1.next_state_function.system_type}

SYSTEM 2 STATE FUNCTION:
Equations: {system2.next_state_function.equations}
Matrix form: {system2.next_state_function.matrix_form}
A matrix: {system2.next_state_function.A_matrix}
B vector: {system2.next_state_function.B_vector}
Type: {system2.next_state_function.system_type}

Analyze structure match, dimension matching, parameter correspondences.
Provide JSON: morphism_type, strength, justification, analysis_points, parameter_correspondence, transformation_equation.
Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'PARTIAL',
                'strength': 0.5,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_StateTrans",
            source="StateTrans_S1",
            target="StateTrans_S2",
            source_component="State Transition Function",
            target_component="State Transition Function",
            morphism_type=response.get('morphism_type', 'PARTIAL'),
            strength=_safe_float_conversion(response.get('strength', 0.5)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', '')
        )

    def analyze_transfer_function_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare transfer functions for frequency domain morphism:

TF 1: {system1.transfer_function.symbolic_form}
- Numerator: {system1.transfer_function.numerator}
- Denominator: {system1.transfer_function.denominator}
- Poles: {system1.transfer_function.poles}
- Zeros: {system1.transfer_function.zeros}
- Order: {system1.transfer_function.order}

TF 2: {system2.transfer_function.symbolic_form}
- Numerator: {system2.transfer_function.numerator}
- Denominator: {system2.transfer_function.denominator}
- Poles: {system2.transfer_function.poles}
- Zeros: {system2.transfer_function.zeros}
- Order: {system2.transfer_function.order}

Analyze: rational function structure, pole/zero correspondence, frequency response equivalence.
Provide JSON: morphism_type, strength, justification, analysis_points, parameter_correspondence, transformation_equation.
Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'PARTIAL',
                'strength': 0.5,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_TransferFunc",
            source="TransferFunc_S1",
            target="TransferFunc_S2",
            source_component="Transfer Function",
            target_component="Transfer Function",
            morphism_type=response.get('morphism_type', 'PARTIAL'),
            strength=_safe_float_conversion(response.get('strength', 0.5)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', '')
        )

    def analyze_interface_morphism(self, system1, system2) -> Morphism:
        prompt = f"""
Compare interface specifications:

INTERFACE 1:
- Input coupling: {system1.interface.input_coupling}
- Output measurement: {system1.interface.output_measurement}
- Boundary conditions: {system1.interface.boundary_conditions}
- Energy expression: {system1.interface.energy_expression}

INTERFACE 2:
- Input coupling: {system2.interface.input_coupling}
- Output measurement: {system2.interface.output_measurement}
- Boundary conditions: {system2.interface.boundary_conditions}
- Energy expression: {system2.interface.energy_expression}

Determine morphism type and strength. Note any information loss.
Provide JSON: morphism_type, strength, justification, analysis_points, parameter_correspondence, transformation_equation, information_loss.
Return VALID JSON ONLY.
"""

        success, response = self.llm.generate_content(prompt, json_mode=True)
        
        if not success:
            response = {
                'morphism_type': 'HOMOMORPHIC',
                'strength': 0.8,
                'justification': 'Analysis unavailable',
                'analysis_points': [],
                'parameter_correspondence': {},
                'transformation_equation': '',
                'information_loss': ''
            }
        elif isinstance(response, str):
            response = json.loads(response)

        return Morphism(
            id="M_Interface",
            source="Interface_S1",
            target="Interface_S2",
            source_component="Interface",
            target_component="Interface",
            morphism_type=response.get('morphism_type', 'HOMOMORPHIC'),
            strength=_safe_float_conversion(response.get('strength', 0.8)),
            justification=response.get('justification', ''),
            analysis_points=response.get('analysis_points', []),
            parameter_map=response.get('parameter_correspondence', {}),
            transformation=response.get('transformation_equation', ''),
            information_loss=response.get('information_loss', '')
        )
