import json
import re
import time # Import time for unique ID generation

class Conversation:
    """
    Manages the state and context of a single systems engineering conversation.

    This class encapsulates the core topic, all generated artifacts, and provides
    structured methods for interacting with the conversation's state. This ensures
    that context is reliably maintained and passed between different parts of the application.
    """
    def __init__(self, system_topic: str):
        """
        Initializes a new conversation.

        Args:
            system_topic (str): The core subject of the system being designed.
        """
        if not system_topic or not isinstance(system_topic, str):
            raise ValueError("System topic must be a non-empty string.")
        self.system_topic = system_topic
        self.artifacts = {}
        self.traces = []  # To store relationships, e.g., [('SR-001', 'SD-001')]
        self._artifact_counter = 0
        
        # Track hard-rule context for follow-up queries
        # Values: None | "rule_1" | "rule_2"
        self.last_rule_triggered = None
        # Store the exact hardcoded response text that was returned
        self.last_hard_rule_response = None
        
        # Track hard-rule context for follow-up queries
        self.last_rule_triggered = None  # None, "rule_1", or "rule_2"
        self.last_hard_rule_response = None  # Store the previous hardcoded response

    def add_artifact(self, artifact_type: str, text: str):
        """
        Adds a new artifact to the conversation. Note: This does not parse traces.
        """
        if not artifact_type or not text:
            return

        artifact_id = self._extract_or_generate_id(artifact_type, text)
        if not artifact_id:
            return

        # Clean the text to remove the redundant header before storing
        print(f"DEBUG: _clean_artifact_text - Original text for {artifact_id}:\n{text[:200]}...")
        cleaned_text = self._clean_artifact_text(artifact_id, text)
        print(f"DEBUG: _clean_artifact_text - Cleaned text for {artifact_id}:\n{cleaned_text[:200]}...")

        self.artifacts[artifact_id] = {
            "id": artifact_id,
            "type": artifact_type,
            "text": cleaned_text,
            "components": self._parse_components(cleaned_text)
        }

    def build_traces(self):
        """
        Builds the traceability links for the entire set of artifacts.
        This should be called AFTER all artifacts have been added.
        """
        self.traces = [] # Reset traces
        all_artifact_ids = set(self.artifacts.keys())

        for source_id, artifact in self.artifacts.items():
            print(f"DEBUG: build_traces - Processing source_id: {source_id}")
            print(f"DEBUG: build_traces - Source artifact text:\n{artifact['text'][:200]}...")
            
            # Regex to find any artifact ID pattern (e.g., SR-123, SD-001)
            trace_pattern = re.compile(r'\b([A-Z]{2}-\d+)\b')
            
            # Find all unique artifact IDs mentioned in the artifact's text
            found_ids = set(trace_pattern.findall(artifact['text']))
            print(f"DEBUG: build_traces - Found IDs in {source_id}'s text: {found_ids}")
            
            for target_id in found_ids:
                # Ensure the target artifact exists, is not the source, and the trace is not a duplicate
                if target_id in all_artifact_ids and source_id != target_id:
                    source_type = self.artifacts[source_id]['type']
                    target_type = self.artifacts[target_id]['type']
                    print(f"DEBUG: build_traces - Considering trace: {source_id} ({source_type}) -> {target_id} ({target_type})")

                    # Define a clear hierarchy for traceability: SR -> SD, SR -> VR, SD -> VR, VR -> VM
                    trace_tuple = None

                    # SR -> SD (Requirement to Design)
                    if source_type == 'SR' and target_type == 'SD':
                        trace_tuple = (source_id, target_id)
                    elif source_type == 'SD' and target_type == 'SR':
                        trace_tuple = (target_id, source_id) # Reverse for consistency

                    # SR -> VR (Requirement to Verification Requirement)
                    elif source_type == 'SR' and target_type == 'VR':
                        trace_tuple = (source_id, target_id)
                    elif source_type == 'VR' and target_type == 'SR':
                        trace_tuple = (target_id, source_id) # Reverse for consistency
                    
                    # SD -> VR (Design to Verification Requirement)
                    elif source_type == 'SD' and target_type == 'VR':
                        trace_tuple = (source_id, target_id)
                    elif source_type == 'VR' and target_type == 'SD':
                        trace_tuple = (target_id, source_id) # Reverse for consistency

                    # VR -> VM (Verification Requirement to Verification Method)
                    elif source_type == 'VR' and target_type == 'VM':
                        trace_tuple = (source_id, target_id)
                    elif source_type == 'VM' and target_type == 'VR':
                        trace_tuple = (target_id, source_id) # Reverse for consistency
                    
                    if trace_tuple and trace_tuple not in self.traces:
                        self.traces.append(trace_tuple)
                        print(f"DEBUG: build_traces - Added trace: {trace_tuple}")
                    elif trace_tuple:
                        print(f"DEBUG: build_traces - Trace {trace_tuple} already exists.")
                    else:
                        print(f"DEBUG: build_traces - No valid Wymorian trace direction for {source_id} ({source_type}) -> {target_id} ({target_type})")

    def _extract_or_generate_id(self, artifact_type: str, text: str) -> str:
        """Helper to get an artifact's ID from its text or create a new one."""
        # Try to extract ID from a header like "### SR-001: Requirement Name"
        match = re.search(r'###\s*([A-Z]{2}-\d+)', text)
        if match:
            return match.group(1)
        
        # Fallback to generating a new ID
        self._artifact_counter += 1
        return f"{artifact_type.upper()}-{self._artifact_counter:03d}"

    def _clean_artifact_text(self, artifact_id: str, text: str) -> str:
        """
        Removes the artifact ID header (e.g., '### SR-001: ') from the artifact text.
        Assumes the LLM output starts with '### ID: Content'.
        """
        # Regex to match "### ID: " at the beginning of the text
        pattern = re.compile(rf"^\s*###\s*{re.escape(artifact_id)}:\s*", re.IGNORECASE)
        cleaned_text = pattern.sub("", text, 1) # Replace only the first occurrence
        return cleaned_text.strip()

    def _parse_components(self, text: str) -> list:
        """
        Helper to parse components from artifact text, assuming a markdown list format.
        Components are identified by lines starting with '- **Component Name:**'.
        Details are subsequent indented lines or lines starting with '-'.
        """
        components = []
        current_component = None
        
        lines = text.split('\n')
        for line in lines:
            stripped_line = line.strip()
            
            # Check for a new component header: '- **Component Name:**'
            component_header_match = re.match(r'^- \*\*(.*?):\*\*', stripped_line)
            if component_header_match:
                if current_component:
                    components.append(current_component)
                component_name = component_header_match.group(1).strip()
                current_component = {"name": component_name, "details": []}
            elif current_component and stripped_line:
                # Add details to the current component.
                # This handles both indented lines and lines starting with '-'
                current_component["details"].append(stripped_line.lstrip('- ').strip())
        
        if current_component:
            components.append(current_component)
            
        return components

    def get_context_for_text_generation(self) -> dict:
        """
        Returns a structured dictionary of the current conversation state,
        formatted for the text generation AI prompt.
        """
        return {
            "system_topic": self.system_topic,
            **self.artifacts
        }

    def get_structured_artifacts(self) -> list:
        """
        Returns a list of all artifacts in a structured format.
        """
        return list(self.artifacts.values())

    def get_all_artifacts(self) -> list:
        """
        Returns a list of all artifact dictionaries.
        """
        return list(self.artifacts.values())

    def get_full_conversation_text(self) -> str:
        """
        Returns the entire conversation history as a single string,
        including the system topic and all artifact texts.
        """
        full_text = f"System Topic: {self.system_topic}\n\n"
        for artifact_id, artifact_data in self.artifacts.items():
            full_text += f"### {artifact_id}: {artifact_data['type']}\n"
            full_text += f"{artifact_data['text']}\n\n"
        return full_text.strip()

    def to_dict(self) -> dict:
        """Serializes the conversation object to a dictionary for session storage."""
        return {
            "system_topic": self.system_topic,
            "artifacts": self.artifacts,
            "traces": self.traces,
            "last_rule_triggered": self.last_rule_triggered,
            "last_hard_rule_response": self.last_hard_rule_response,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserializes a dictionary back into a Conversation object."""
        if not data or 'system_topic' not in data:
            return None
        
        conversation = cls(data['system_topic'])
        conversation.artifacts = data.get('artifacts', {})
        conversation.traces = data.get('traces', [])
        conversation.last_rule_triggered = data.get('last_rule_triggered', None)
        conversation.last_hard_rule_response = data.get('last_hard_rule_response', None)
        
        # Re-initialize counter to avoid ID collisions
        max_counter = 0
        if conversation.artifacts:
            for art_id in conversation.artifacts.keys():
                match = re.search(r'-(\d+)', art_id)
                if match:
                    try:
                        num = int(match.group(1))
                        if num > max_counter:
                            max_counter = num
                    except ValueError:
                        continue
        conversation._artifact_counter = max_counter
        
        return conversation
