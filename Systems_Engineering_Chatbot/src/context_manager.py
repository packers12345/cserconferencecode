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

                    # Determine the correct trace direction based on Wymorian definitions
                    trace_tuple = None

                    # Case 1: Requirement-to-Design (R -> D)
                    # If a Design (SD) mentions a Requirement (SR), we want (SR, SD)
                    if source_type == 'SD' and target_type == 'SR':
                        trace_tuple = (target_id, source_id) # (SR, SD)
                    # If a Requirement (SR) mentions a Design (SD), we want (SR, SD)
                    elif source_type == 'SR' and target_type == 'SD':
                        trace_tuple = (source_id, target_id) # (SR, SD)

                    # Case 2: Requirement-to-Verification (R -> V)
                    # If a Verification (VR/VM) mentions a Requirement (SR), we want (SR, VR/VM)
                    elif source_type in ['VR', 'VM'] and target_type == 'SR':
                        trace_tuple = (target_id, source_id) # (SR, VR/VM)
                    # If a Requirement (SR) mentions a Verification (VR/VM), we want (SR, VR/VM)
                    elif source_type == 'SR' and target_type in ['VR', 'VM']:
                        trace_tuple = (source_id, target_id) # (SR, VR/VM)

                    # Case 3: Design-to-Verification (D -> V)
                    # If a Verification (VR/VM) mentions a Design (SD), we want (SD, VR/VM)
                    elif source_type in ['VR', 'VM'] and target_type == 'SD':
                        trace_tuple = (target_id, source_id) # (SD, VR/VM)
                    # If a Design (SD) mentions a Verification (VR/VM), we want (SD, VR/VM)
                    elif source_type == 'SD' and target_type in ['VR', 'VM']:
                        trace_tuple = (source_id, target_id) # (SD, VR/VM)
                    
                    if trace_tuple:
                        print(f"DEBUG: build_traces - Proposed trace_tuple: {trace_tuple}")
                        if trace_tuple not in self.traces:
                            self.traces.append(trace_tuple)
                            print(f"DEBUG: build_traces - Added trace: {trace_tuple}")
                        else:
                            print(f"DEBUG: build_traces - Trace {trace_tuple} already exists.")
                    else:
                        print(f"DEBUG: build_traces - No valid Wymorian trace direction for {source_id} -> {target_id}")

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
        Removes the redundant header (e.g., 'SR-001: ### SR-001: ') from the artifact text.
        """
        # Regex to match the pattern "ID: ### ID: " at the beginning of the text
        # It handles cases where the ID might be followed by a colon and then "### ID:"
        pattern = re.compile(rf"^{re.escape(artifact_id)}:\s*###\s*{re.escape(artifact_id)}:\s*", re.IGNORECASE)
        cleaned_text = pattern.sub("", text, 1) # Replace only the first occurrence
        return cleaned_text.strip()

    def _parse_components(self, text: str) -> list:
        """Helper to parse components from artifact text."""
        components = []
        # This regex captures lines that start with '- **' as component names
        # and then captures subsequent lines that are indented or start with '-' as details.
        component_pattern = re.compile(r'^- \*\*(.*?):\*\*(.*?(?=\n^- \*\*|\Z))', re.DOTALL | re.MULTILINE)
        
        matches = component_pattern.finditer(text)
        for match in matches:
            component_name = match.group(1).strip()
            details_block = match.group(2).strip()
            
            details = []
            # Split the details block by lines and add non-empty, non-component lines as details
            for line in details_block.split('\n'):
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('- **'):
                    details.append(stripped_line)
            
            components.append({"name": component_name, "details": details})
        
        # Fallback for simpler component parsing if the above regex is too strict or for different formats
        if not components:
            current_component = None
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('- **'):
                    if current_component:
                        components.append(current_component)
                    component_name = line.split('**')[1].strip(':') # Remove trailing colon
                    current_component = {"name": component_name, "details": []}
                elif line.startswith('-') and current_component:
                    # Add any line starting with '-' as a detail if a component is active
                    current_component["details"].append(line.lstrip('- ').strip())
                elif current_component and line:
                    # Add any non-empty line as a detail if a component is active (for multi-line details)
                    current_component["details"].append(line)
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

    def to_dict(self) -> dict:
        """Serializes the conversation object to a dictionary for session storage."""
        return {
            "system_topic": self.system_topic,
            "artifacts": self.artifacts,
            "traces": self.traces
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserializes a dictionary back into a Conversation object."""
        if not data or 'system_topic' not in data:
            return None
        
        conversation = cls(data['system_topic'])
        conversation.artifacts = data.get('artifacts', {})
        conversation.traces = data.get('traces', [])
        
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
