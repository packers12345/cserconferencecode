import os
import json
import time
from openai import OpenAI, RateLimitError, APIError
from .env_utils import safe_load_dotenv
from .context_manager import Conversation
from .prompts import (
    get_homomorphism_proof_prompt,
    get_isomorphism_justification_prompt,
    get_graph_generation_prompt,
    get_l1_mapping_prompt,
    get_morphism_proof_prompt_template # New import
)
from .morphism_proof_data import MORPHISM_PROOF_DATA # Changed to relative import

# Load environment variables from the .env file using a safe loader
safe_load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class GeminiClient:
    """A client for interacting with OpenAI's API (GPT models).
    
    Note: Class name kept as GeminiClient for backward compatibility with existing code,
    but it now uses OpenAI's API instead of Google's Gemini API.
    """

    def __init__(self, model_name='gpt-4o-mini', max_retries=5, base_delay=1):
        """
        Initializes the OpenAI client.

        Args:
            model_name (str): The name of the OpenAI model to use (default: gpt-4o-mini).
            max_retries (int): The maximum number of retries for API calls.
            base_delay (int): The base delay in seconds for exponential backoff.
        """
        self.model_name = model_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._configure_api()

    def _configure_api(self):
        """Configures the OpenAI API with the API key."""
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            print("Warning: OPENAI_API_KEY not set. Client will be disabled until an API key is provided.")
            self.enabled = False
            self.client = None
            return
        try:
            self.client = OpenAI(api_key=openai_api_key)
            self.enabled = True
        except Exception as e:
            print(f"Error configuring OpenAI client: {e}")
            self.enabled = False
            self.client = None

    def generate_content(self, prompt: str, json_mode: bool = False) -> tuple[bool, str | dict]:
        """
        Generates content using OpenAI's API with retry logic.

        Args:
            prompt (str): The prompt to send to the model.
            json_mode (bool): Whether to request a JSON response.

        Returns:
            tuple[bool, str | dict]: A tuple containing a success flag and the response text or a dictionary.
        """
        if not getattr(self, 'enabled', False) or not self.client:
            return False, "OpenAI client is not configured. Set OPENAI_API_KEY in your environment to enable generation."

        retries = 0
        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} if json_mode else {"type": "text"}
                )
                
                response_text = response.choices[0].message.content
                
                if json_mode:
                    return True, json.loads(response_text)
                return True, response_text

            except RateLimitError as e:
                retries += 1
                delay = self.base_delay * (2 ** (retries - 1))
                print(f"Rate limit error: {e}. Retrying in {delay}s (attempt {retries}/{self.max_retries}).")
                time.sleep(delay)
            except APIError as e:
                retries += 1
                delay = self.base_delay * (2 ** (retries - 1))
                print(f"API error: {e}. Retrying in {delay}s (attempt {retries}/{self.max_retries}).")
                time.sleep(delay)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return False, str(e)
        
        return False, f"Failed to generate content after {self.max_retries} attempts."

def generate_morphism_proof(conversation: Conversation, system_b_description: str, gemini_client: GeminiClient) -> str:
    """Generates a morphism proof using the Gemini API."""
    system_a_description = conversation.system_topic
    prompt = get_homomorphism_proof_prompt(
        system_a_description=system_a_description,
        system_b_description=system_b_description
    )
    
    success, result = gemini_client.generate_content(prompt)
    if not success:
        return f"### Error\n{result}"
    conversation.add_artifact("morphism_proof", result)
    return result

def generate_isomorphism_justification(system_x_description: str, system_y_description: str, gemini_client: GeminiClient) -> str:
    """
    Generates an isomorphism justification using the Gemini API,
    including the structured morphism proof as context.
    """
    morphism_proof_context = get_formatted_morphism_proof()
    
    prompt = get_isomorphism_justification_prompt(
        system_x_description=system_x_description,
        system_y_description=system_y_description,
        morphism_proof_context=morphism_proof_context
    )
    
    success, result = gemini_client.generate_content(prompt)
    if not success:
        return f"### Error\n{result}"
    return result

def generate_graph_from_text(conversation: Conversation, gemini_client: GeminiClient) -> dict:
    """Generates a graph visualization from the full text of a Conversation object."""
    full_text = conversation.get_full_conversation_text()
    prompt = get_graph_generation_prompt(
        system_topic=conversation.system_topic,
        full_text=full_text
    )
    
    success, result = gemini_client.generate_content(prompt, json_mode=True)
    if not success:
        return {"graph_data": {"nodes": [{"id": "error", "label": "Graph Error", "title": result}], "edges": []}}
    return result

def generate_l1_mapping(system_a: str, system_b: str, gemini_client: GeminiClient) -> str:
    """Generate a structured L1 mapping (morphism) between two abstract system models."""
    prompt = get_l1_mapping_prompt(system_a=system_a, system_b=system_b)
    
    success, result = gemini_client.generate_content(prompt, json_mode=False) # Changed to json_mode=False for narrative output
    if not success:
        return f"### Error\n{result}" # Return error as string
    return result

def get_formatted_morphism_proof() -> str:
    """
    Formats the MORPHISM_PROOF_DATA into a human-readable string for prompt inclusion.
    """
    proof_data = MORPHISM_PROOF_DATA
    formatted_output = []

    formatted_output.append(f"### Morphism Proof: {proof_data['system_topic']}")
    formatted_output.append("\nThis document outlines the formal proof of a morphism between a mass-spring-damper system and an RLC circuit, demonstrating their mathematical analogy.")

    formatted_output.append("\n#### 1. Governing Differential Equations")
    formatted_output.append(f"**Mechanical System ({proof_data['mechanical_system']['name']}):**")
    formatted_output.append(f"Equation: `{proof_data['mechanical_system']['differential_equation']}`")
    formatted_output.append(f"Symbolic States: {', '.join(proof_data['mechanical_system']['symbolic_states'])}")

    formatted_output.append(f"\n**Electrical System ({proof_data['electrical_system']['name']}):**")
    formatted_output.append(f"Equation: `{proof_data['electrical_system']['differential_equation']}`")
    formatted_output.append(f"Symbolic States: {', '.join(proof_data['electrical_system']['symbolic_states'])}")

    formatted_output.append("\n#### 2. Correspondence between Variables and Parameters")
    formatted_output.append("| Mechanical | Electrical |")
    formatted_output.append("|---|---|")
    for mech_var, elec_var in proof_data['variable_correspondence'].items():
        formatted_output.append(f"| {mech_var} | {elec_var} |")

    formatted_output.append("\n#### 3. States and Interfaces Description")
    formatted_output.append("\n**Mechanical System:**")
    formatted_output.append(f"- States: {proof_data['state_interface_description']['mechanical']['states']}")
    formatted_output.append(f"- Input: {proof_data['state_interface_description']['mechanical']['input']}")
    formatted_output.append(f"- Outputs: {proof_data['state_interface_description']['mechanical']['outputs']}")
    formatted_output.append(f"- Next State Function: {proof_data['state_interface_description']['mechanical']['next_state_function']}")

    formatted_output.append("\n**Electrical System:**")
    formatted_output.append(f"- States: {proof_data['state_interface_description']['electrical']['states']}")
    formatted_output.append(f"- Inputs: {proof_data['state_interface_description']['electrical']['inputs']}")
    formatted_output.append(f"- Outputs: {proof_data['state_interface_description']['electrical']['outputs']}")
    formatted_output.append(f"- Next State Function: {proof_data['state_interface_description']['electrical']['next_state_function']}")

    return "\n".join(formatted_output)
