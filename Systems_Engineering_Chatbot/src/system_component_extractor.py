import json
import logging
import os
from Systems_Engineering_Chatbot.src.api_integration import GeminiClient
from Systems_Engineering_Chatbot.src.prompts import get_single_system_extraction_prompt

# Configure logging
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
logger = logging.getLogger(__name__)

class ComponentSpec:
    """
    A generic wrapper for system sub-components to provide safe attribute access.
    """
    def __init__(self, data: dict = None):
        self._data = data if data is not None else {}
        # Common attributes across various component types
        self.symbol = self._data.get('symbol', 'N/A')
        self.description = self._data.get('description', 'N/A')
        self.domain = self._data.get('domain', 'N/A')
        self.units = self._data.get('units', 'N/A')
        self.equation = self._data.get('equation', 'N/A')
        self.constraints = self._data.get('constraints', 'N/A')
        
        # State Variables specific attributes
        # Changed 'description' (singular) to 'descriptions' (plural list)
        self.symbols = self._data.get('symbols', ['N/A'])
        self.descriptions = self._data.get('descriptions', ['N/A']) # Added this line
        self.dimension = self._data.get('dimension', 0)
        self.vector_form = self._data.get('vector_form', 'N/A')

        # Next State Function specific attributes
        self.equations = self._data.get('equations', 'N/A')
        self.matrix_form = self._data.get('matrix_form', 'N/A')
        self.A_matrix = self._data.get('A_matrix', 'N/A')
        self.B_vector = self._data.get('B_vector', 'N/A')
        self.coefficients = self._data.get('coefficients', {})
        self.order = self._data.get('order', 'N/A')
        self.system_type = self._data.get('system_type', 'N/A')

        # Transfer Function specific attributes
        self.symbolic_form = self._data.get('symbolic_form', 'N/A')
        self.numerator = self._data.get('numerator', [])
        self.denominator = self._data.get('denominator', [])
        self.poles = self._data.get('poles', 'N/A')
        self.zeros = self._data.get('zeros', 'N/A')
        self.DC_gain = self._data.get('DC_gain', 'N/A')

        # Interface specific attributes
        self.input_coupling = self._data.get('input_coupling', 'N/A')
        self.output_measurement = self._data.get('output_measurement', 'N/A')
        self.boundary_conditions = self._data.get('boundary_conditions', [])
        self.energy_expression = self._data.get('energy_expression', 'N/A')

    def to_dict(self) -> dict:
        return self._data

class ExtractedSystemSpec:
    """
    A wrapper class to access extracted system components as attributes,
    and provide a .to_dict() method for caching.
    All sub-components are also wrapped in ComponentSpec for safe access.
    """
    def __init__(self, data: dict):
        self._data = data
        self.system_name = data.get('system_name', 'N/A')
        self.input = ComponentSpec(data.get('input'))
        self.output = ComponentSpec(data.get('output'))
        self.state_variables = ComponentSpec(data.get('state_variables'))
        self.next_state_function = ComponentSpec(data.get('next_state_function'))
        self.transfer_function = ComponentSpec(data.get('transfer_function'))
        self.interface = ComponentSpec(data.get('interface'))

    def to_dict(self) -> dict:
        # Return the original raw data for caching, as it's already JSON-serializable
        return self._data

class SystemComponentExtractor:
    """
    Extracts structured system component information from a natural language description.
    """
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def extract_system_specification(self, system_name: str, expert_documentation: str = "") -> ExtractedSystemSpec:
        """
        Extracts system components (input, output, state_variables, next_state_function,
        transfer_function, interface) from a system description using the LLM.

        Args:
            system_name (str): The name or description of the system.
            expert_documentation (str): Optional expert documentation to guide the LLM.

        Returns:
            ExtractedSystemSpec: An object containing the extracted system components.
        """
        prompt = get_single_system_extraction_prompt(system_name, expert_documentation)
        logger.info(f"Generated prompt for SystemComponentExtractor: {prompt}")

        try:
            success, raw_response_or_error = self.gemini_client.generate_content(prompt, json_mode=True)
            
            if not success:
                logger.error(f"LLM generation failed for '{system_name}': {raw_response_or_error}")
                raise ValueError(f"LLM generation failed: {raw_response_or_error}")

            raw_response = raw_response_or_error # Now raw_response is guaranteed to be the dict/string from LLM
            logger.debug(f"Raw LLM response for system component extraction: {raw_response}")

            system_spec_dict = raw_response # If json_mode=True, generate_content returns a dict directly
            
            # Additional check if LLM returned a string that needs parsing (e.g., if json_mode was ignored or failed internally)
            if isinstance(raw_response, str):
                if raw_response.strip().startswith("```json"):
                    json_string = raw_response.strip()[7:-3].strip()
                else:
                    json_string = raw_response.strip()
                system_spec_dict = json.loads(json_string)
            
            # Return an instance of the new wrapper class
            return ExtractedSystemSpec(system_spec_dict)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in extract_system_specification: {e}")
            logger.error(f"Raw LLM response causing error: {raw_response}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            logger.error(f"Error during system component extraction for '{system_name}': {e}")
            raise
