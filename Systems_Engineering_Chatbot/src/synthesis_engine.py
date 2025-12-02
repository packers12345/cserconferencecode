import os
import json
from Systems_Engineering_Chatbot.src.pdf_processor import extract_tables_from_pdf
from Systems_Engineering_Chatbot.src.systems_mathematics import SystemModel, State, Input, Output, InterfaceFunction, IsomorphismChecker
from Systems_Engineering_Chatbot.src.api_integration import GeminiClient
from Systems_Engineering_Chatbot.src.prompts import get_synthesis_prompt, get_traceability_matrix_prompt

class SynthesisEngine:
    def __init__(self, pdf_path: str, gemini_client: GeminiClient = None):
        self.pdf_path = pdf_path
        self.gemini_client = gemini_client

    def generate_response(self, prompt: str, conversation_context: dict) -> str:
        """
        Generates a Wymorian-based algebraic structure for a given system.
        """
        system_topic = conversation_context.get("system_topic", "the specified system")

        # Fallback: existing behavior using the LLM client (if available)
        wymorian_prompt = get_synthesis_prompt(prompt, system_topic)

        try:
            if not self.gemini_client:
                return "### Error\nNo AI client configured for synthesis generation."
            success, response_text = self.gemini_client.generate_content(wymorian_prompt)
            if not success:
                return f"### Error\nAn error occurred during synthesis: {response_text}"
            return response_text
        except Exception as e:
            print(f"ERROR in SynthesisEngine: {e}")
            return f"### Error\nAn error occurred during synthesis: {e}"

    def generate_traceability_matrix(self, system_topic: str) -> str:
        """
        Generates a complete, deterministic Wymorian Traceability Matrix from a single prompt.
        """
        matrix_prompt = get_traceability_matrix_prompt(system_topic)

        try:
            success, response_text = self.gemini_client.generate_content(matrix_prompt)
            if not success:
                return f"### Error\nAn error occurred during matrix generation: {response_text}"
            return response_text
        except Exception as e:
            print(f"ERROR in SynthesisEngine matrix generation: {e}")
            return f"### Error\nAn error occurred during matrix generation: {e}"

if __name__ == '__main__':
    # This is for testing purposes.
    pdf_file_path = os.path.join(os.path.dirname(__file__), '..', 'Wach_PF_D_2023 (1).pdf')
    
    # Initialize GeminiClient for testing
    test_gemini_client = GeminiClient()
    engine = SynthesisEngine(pdf_file_path, test_gemini_client)

    # Example prompt and context
    test_prompt = "what is the verification requirements for a drone delivery system"
    test_context = {
        "system_topic": "drone delivery system",
    }

    # Generate a response
    generated_response = engine.generate_response(test_prompt, test_context)
    print("Generated Response:\n", generated_response)
