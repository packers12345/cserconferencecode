import os
import re
import json
import base64
import requests
import PyPDF2
import spacy
import graphviz
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
import math
from neo4j import GraphDatabase, basic_auth # Import Neo4j driver components

# Note: pyvis and networkx are imported but not used in the provided functions.
# Keeping them if you intend to add network visualization functionality later.
from pyvis.network import Network
import networkx as nx

# Load environment variables at the very beginning of the script execution
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'. This will happen once.")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Gemini API Configuration ---
def get_gemini_client():
    """
    Retrieves the Gemini API key from environment variables and configures the Gemini client.
    Returns the configured generative model instance.
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel('gemini-1.5-flash') # Using a fast model for text generation

# --- Neo4j Integration ---
class Neo4jConnector:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None
        self._connect()

    def _connect(self):
        try:
            self._driver = GraphDatabase.driver(self._uri, auth=basic_auth(self._user, self._password))
            self._driver.verify_connectivity()
            print("Neo4j connection established.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self._driver = None # Ensure driver is None if connection fails

    def close(self):
        if self._driver:
            self._driver.close()
            print("Neo4j connection closed.")

    def execute_query(self, query, parameters=None):
        """Executes a Cypher query and returns the results."""
        if not self._driver:
            print("Neo4j driver not initialized. Attempting to reconnect...")
            self._connect() # Try to reconnect if driver is None
            if not self._driver: # If reconnection still fails
                print("Neo4j connection still unavailable. Cannot execute query.")
                return []

        with self._driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Error executing Neo4j query: {e}")
                return []

# Initialize Neo4j connector globally (or pass as needed)
neo4j_uri = os.environ.get("NEO4J_URI")
neo4j_username = os.environ.get("NEO4J_USERNAME")
neo4j_password = os.environ.get("NEO4J_PASSWORD")

neo4j_connector = None
if neo4j_uri and neo4j_username and neo4j_password:
    neo4j_connector = Neo4jConnector(neo4j_uri, neo4j_username, neo4j_password)
else:
    print("Neo4j environment variables not fully set. Neo4j integration will be skipped.")

# --- PDF Processing ---
def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    Extracts text from a PDF file.
    Args:
        pdf_file: A BytesIO object containing the PDF data.
    Returns:
        A string containing all extracted text from the PDF.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# --- Helper for AI Generation (moved from app.py to here for reusability) ---
def generate_content_with_ai(prompt: str, system_prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """
    Generates content using the Gemini AI model with a system prompt and optional PDF context.
    """
    model = get_gemini_client()
    full_prompt_parts = []
    
    # Add PDF text if available
    if pdf_data:
        pdf_text = extract_text_from_pdf(pdf_data)
        if pdf_text:
            full_prompt_parts.append(f"Context from PDF:\n{pdf_text}\n\n")

    full_prompt_parts.append(f"System Prompt: {system_prompt}\n\nUser Query: {prompt}")

    try:
        response = model.generate_content("".join(full_prompt_parts))
        return response.text
    except Exception as e:
        print(f"Error generating AI content for prompt '{prompt[:50]}...': {e}")
        return f"AI generation failed: {e}"

# --- Specific Generation Functions ---

def generate_system_requirements(prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """Generates system requirements based on a prompt, with optional PDF context."""
    system_prompt = "As a Systems Engineering AI, generate detailed functional and non-functional system requirements for the following system description, ensuring they are clear, concise, verifiable, and traceable. Categorize them appropriately (e.g., Functional, Performance, Security, Usability, etc.)."
    return generate_content_with_ai(prompt, system_prompt, pdf_data)

def generate_system_designs(prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """Generates system design concepts based on a prompt, with optional PDF context."""
    system_prompt = "As a Systems Engineering AI, propose a high-level system architecture and design concepts for the following system description. Include key components, their interactions, and technologies. Focus on modularity and scalability."
    return generate_content_with_ai(prompt, system_prompt, pdf_data)

def create_verification_requirements_models(prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """Generates verification requirements based on system requirements/design, with optional PDF context."""
    system_prompt = "As a Systems Engineering AI, create comprehensive verification requirements for the system described, derived from its system requirements and design. Each verification requirement should specify what needs to be verified and how (e.g., Test, Inspection, Analysis, Demonstration)."
    return generate_content_with_ai(prompt, system_prompt, pdf_data)

def get_traceability(prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """Generates a traceability matrix/analysis based on system requirements, design, and verification, with optional PDF context."""
    system_prompt = "As a Systems Engineering AI, generate a traceability matrix or analysis demonstrating the links between system requirements, system design components, and verification requirements for the given system description. Highlight how each requirement is addressed in the design and verified."
    return generate_content_with_ai(prompt, system_prompt, pdf_data)

def get_verification_conditions(prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """Generates verification conditions/test cases based on verification requirements, with optional PDF context."""
    system_prompt = "As a Systems Engineering AI, define detailed verification conditions, test cases, or test procedures for the system based on its verification requirements. Include preconditions, steps, expected outcomes, and pass/fail criteria."
    return generate_content_with_ai(prompt, system_prompt, pdf_data)

# --- Graph Visualization Logic ---

def create_enhanced_fallback_graph_data() -> dict:
    """
    Creates enhanced fallback graph data (nodes, edges, configurations)
    with a central node and concentric rings.
    """
    nodes = {
        "SR": {"label": "System Requirements", "type": "requirement", "ring": 0},
        "SD": {"label": "System Design", "type": "design", "ring": 1},
        "VR": {"label": "Verification Requirements", "type": "verification", "ring": 2},
        "VM": {"label": "Verification Methods", "type": "method", "ring": 3},
        "TM": {"label": "Traceability Matrix", "type": "traceability", "ring": 0}, # Central with SR
    }
    edges = [
        {"from": "SR", "to": "SD", "label": "realizes"},
        {"from": "SR", "to": "VR", "label": "verified by"},
        {"from": "SD", "to": "VR", "label": "verifies"},
        {"from": "VR", "to": "VM", "label": "implemented by"},
        {"from": "SR", "to": "TM", "label": "traced in"},
        {"from": "SD", "to": "TM", "label": "traced in"},
        {"from": "VR", "to": "TM", "label": "traced in"},
        {"from": "VM", "to": "TM", "label": "traced in"},
    ]
    return {"nodes": nodes, "edges": edges}

def calculate_positions_for_rings(graph_data: dict, center_node_ids: List[str] = ['SR', 'TM']) -> Dict[str, Tuple[float, float]]:
    """
    Calculates fixed positions for nodes based on concentric rings,
    with specified nodes at the center.
    """
    positions = {}
    nodes_by_ring = {}
    for node_id, config in graph_data['nodes'].items():
        ring = config.get('ring', 0)
        if ring not in nodes_by_ring:
            nodes_by_ring[ring] = []
        nodes_by_ring[ring].append(node_id)

    # Sort rings to process from center outwards
    sorted_rings = sorted(nodes_by_ring.keys())

    for ring in sorted_rings:
        node_ids = nodes_by_ring[ring]
        radius = ring * 150 + 50 # Base radius for each ring

        if ring == 0:
            # Handle center nodes
            center_nodes_in_ring = [n_id for n_id in node_ids if n_id in center_node_ids]
            other_nodes_in_ring = [n_id for n_id in node_ids if n_id not in center_node_ids]

            if not center_nodes_in_ring:
                # If no specified center nodes in ring 0, pick first
                center_nodes_in_ring = [node_ids[0]] if node_ids else []

            if len(center_nodes_in_ring) == 1:
                positions[center_nodes_in_ring[0]] = (0, 0)
            else:
                # Arrange multiple center nodes in a small circle
                for i, node_id in enumerate(center_nodes_in_ring):
                    angle = 2 * math.pi * i / len(center_nodes_in_ring)
                    x = 50 * math.cos(angle)  # Small radius for center cluster
                    y = 50 * math.sin(angle)
                    positions[node_id] = (x, y)

            # Arrange other nodes in ring 0 around the center cluster
            if other_nodes_in_ring:
                start_angle = 0 if len(center_nodes_in_ring) <= 1 else (2 * math.pi / len(center_nodes_in_ring) / 2)
                for i, node_id in enumerate(other_nodes_in_ring):
                    angle = start_angle + (2 * math.pi * i / len(other_nodes_in_ring))
                    x = (radius * 0.7) * math.cos(angle) # Slightly smaller radius for these
                    y = (radius * 0.7) * math.sin(angle)
                    positions[node_id] = (x, y)

        else:
            # Arrange nodes in a circle at the specified radius
            for i, node_id in enumerate(node_ids):
                angle = 2 * math.pi * i / len(node_ids)
                # Add some offset based on group to prevent overlap
                group_offset = ring * 0.1 # Small offset per ring
                angle += group_offset

                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                positions[node_id] = (x, y)

    return positions

# Update the existing fallback function to use enhanced structure
def create_web_fallback_graph_data() -> dict:
    """Creates enhanced fallback graph when AI generation fails - updated to use enhanced structure"""
    return create_enhanced_fallback_graph_data()

def create_fallback_graph_data(system_design: str, verification_requirements: str) -> dict:
    """
    Creates enhanced fallback graph when AI generation fails - updated to use enhanced structure.
    This function is primarily for backward compatibility if older calls expect it.
    """
    # In a real scenario, you might parse system_design/verification_requirements
    # to create a more relevant fallback, but for simplicity, we return the generic one.
    return create_enhanced_fallback_graph_data()


# --- Modified generate_network_visualization to integrate Neo4j ---
def generate_network_visualization(user_prompt: str, pdf_data: Optional[BytesIO] = None) -> str:
    """
    Generates a network visualization (graph) based on the provided prompt and PDF data.
    This function will internally generate System Design, Verification Requirements,
    Traceability, and Verification Conditions. It can also integrate Neo4j insights.
    """
    try:
        # Step 1: Internally generate core system engineering artifacts
        print("Generating core system engineering artifacts for visualization context...")
        system_design_text = generate_system_designs(user_prompt, pdf_data=pdf_data)
        verification_requirements_text = create_verification_requirements_models(user_prompt, pdf_data=pdf_data)
        traceability_text = get_traceability(user_prompt, pdf_data=pdf_data)
        verification_conditions_text = get_verification_conditions(user_prompt, pdf_data=pdf_data)

        # Step 2: Attempt to fetch data from Neo4j if connector is available and prompt suggests it
        neo4j_data_context = ""
        if neo4j_connector:
            if "neo4j" in user_prompt.lower() or "graph database" in user_prompt.lower():
                print("Attempting to query Neo4j for additional context...")
                # Example generic query: fetch some nodes and relationships
                # You might need to make this more specific based on your Neo4j schema
                cypher_query = "MATCH (n)-[r]-(m) RETURN n, type(r) AS relType, m LIMIT 20"
                neo4j_records = neo4j_connector.execute_query(cypher_query)

                if neo4j_records:
                    nodes_from_neo4j = set()
                    relationships_from_neo4j = []
                    for record in neo4j_records:
                        start_node = record["n"]
                        end_node = record["m"]
                        rel_type = record["relType"]

                        # Extract properties as dictionary, ensuring they are JSON serializable
                        start_node_props = dict(start_node)
                        end_node_props = dict(end_node)

                        nodes_from_neo4j.add(json.dumps({"id": start_node.id, "labels": list(start_node.labels), "properties": start_node_props}))
                        nodes_from_neo4j.add(json.dumps({"id": end_node.id, "labels": list(end_node.labels), "properties": end_node_props}))
                        relationships_from_neo4j.append(f"({start_node.id})-[:{rel_type}]->({end_node.id})")

                    neo4j_nodes_str = "\n".join(sorted(list(nodes_from_neo4j)))
                    neo4j_relationships_str = "\n".join(relationships_from_neo4j)
                    neo4j_data_context = (
                        f"\n\nAdditional context from Neo4j graph database:\n"
                        f"Nodes:\n{neo4j_nodes_str}\n"
                        f"Relationships:\n{neo44_relationships_str}\n"
                        f"Please consider this data when generating the visualization or insights."
                    )
                else:
                    print("No data retrieved from Neo4j or query failed.")
                    neo4j_data_context = "\n\nCould not retrieve data from Neo4j. It might be empty or inaccessible."
            else:
                print("Neo4j query not explicitly requested in prompt. Skipping Neo4j data fetch.")
        else:
            print("Neo4j connector not initialized. Skipping Neo4j data fetch.")

        # Step 3: Combine all relevant text into a single prompt for the AI to generate graph details
        combined_ai_prompt = (
            f"User's primary request: {user_prompt}\n\n"
            f"Here are the internally generated system engineering artifacts:\n"
            f"System Design: {system_design_text}\n\n"
            f"Verification Requirements: {verification_requirements_text}\n\n"
            f"Traceability: {traceability_text}\n\n"
            f"Verification Conditions: {verification_conditions_text}\n"
            f"{neo4j_data_context}" # Include Neo4j context here
            f"\n\nBased on all the provided information (user's request, generated artifacts, and optional Neo4j data),"
            f"generate a detailed description of nodes and edges for a system visualization graph."
            f"The output should be a JSON array of objects, where each object represents either a 'node' or an 'edge'."
            f"Nodes should have 'id', 'label', and 'type'. Edges should have 'from', 'to', and 'label'."
            f"Focus on key components, relationships, and traceability aspects."
            f"Example for Node: {{ \"id\": \"NodeA\", \"label\": \"Component A\", \"type\": \"component\" }}"
            f"Example for Edge: {{ \"from\": \"NodeA\", \"to\": \"NodeB\", \"label\": \"connects to\" }}"
            f"Ensure the graph can represent system architecture, requirements, and verification flows."
            f"If Neo4j data was provided, incorporate relevant nodes and relationships from it into the graph where appropriate,"
            f"especially if they represent architectural components or dependencies."
            f"If the request is for a 'system architecture' specifically, emphasize components and their connections."
            f"If the request is for 'traceability', emphasize requirements, design, and verification links."
            f"Keep the graph concise yet informative, focusing on the most critical elements."
        )

        model = get_gemini_client()
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING", "description": "Unique identifier for the node or edge."},
                    "label": {"type": "STRING", "description": "Display label for the node or edge."},
                    "type": {"type": "STRING", "enum": ["node", "edge"], "description": "Type of the element: 'node' or 'edge'."},
                    "from": {"type": "STRING", "description": "Source node ID for an edge (only for edges)."},
                    "to": {"type": "STRING", "description": "Target node ID for an edge (only for edges)."}
                },
                "required": ["type", "id", "label"]
            }
        }

        print("Sending combined prompt to AI for graph data generation...")
        ai_response = model.generate_content(
            combined_ai_prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
        )
        
        # Ensure the response text is a string before parsing
        if isinstance(ai_response.text, str):
            graph_elements = json.loads(ai_response.text)
        else:
            print(f"AI response text is not a string: {type(ai_response.text)}")
            graph_elements = []


        # --- Build Graphviz graph from AI-generated elements ---
        dot = graphviz.Digraph(comment='System Visualization', format='svg')
        dot.attr(rankdir='LR') # Left to Right
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='#E0F7FA', fontname='Helvetica', fontsize='12')
        dot.attr('edge', fontname='Helvetica', fontsize='10', color='#616161')

        # Collect nodes and edges
        nodes_dict = {}
        edges_list = []

        for element in graph_elements:
            if element.get("type") == "node":
                nodes_dict[element["id"]] = element
            elif element.get("type") == "edge":
                edges_list.append(element)

        # Add nodes to graphviz
        for node_id, node_data in nodes_dict.items():
            fill_color = '#BBDEFB' # Default color
            if 'requirement' in node_data.get('type', '').lower():
                fill_color = '#C8E6C9'
            elif 'design' in node_data.get('type', '').lower():
                fill_color = '#FFECB3'
            elif 'verification' in node_data.get('type', '').lower() or 'method' in node_data.get('type', '').lower():
                fill_color = '#D1C4E9'
            elif 'database' in node_data.get('type', '').lower() or 'neo4j' in node_data.get('type', '').lower():
                fill_color = '#A7FFEB' # Light cyan for DB nodes
            dot.node(node_id, node_data.get('label', node_id), fillcolor=fill_color)

        # Add edges to graphviz
        for edge_data in edges_list:
            if edge_data['from'] in nodes_dict and edge_data['to'] in nodes_dict:
                dot.edge(edge_data['from'], edge_data['to'], label=edge_data.get('label', ''))
            else:
                print(f"Skipping edge due to missing node: {edge_data}")


        # Render the graph to SVG string
        svg_output = dot.pipe(format='svg').decode('utf-8')
        return svg_output

    except json.JSONDecodeError as e:
        print(f"JSON parsing error from AI response: {e}. Raw response: {ai_response.text}")
        return f"<svg width='400' height='100'><text x='10' y='50' fill='red'>Error: AI did not return valid graph JSON. Details: {e}</text></svg>"
    except Exception as e:
        print(f"Error generating network visualization: {e}")
        # Return a simple error message or placeholder SVG
        return f"<svg width='400' height='100'><text x='10' y='50' fill='red'>An error occurred during graph generation: {e}</text></svg>"

