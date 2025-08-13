# -*- coding: utf-8 -*-
"""
Generative Graph Creator for Wymorian Systems Engineering Chatbot.

This module creates a hierarchical, tree-like graph visualization for a
given system topic. The graph is generated dynamically, with content-aware
nodes created by an LLM and a randomized structure to ensure a robust,
full visualization.
"""
import random
import json
from api_integration import get_gemini_client

def create_full_system_graph(system_topic: str) -> dict:
    """
    Generates a full, hierarchical system graph using a single, monolithic
    LLM prompt to ensure atomicity and robustness. The content is generated
    specifically for the system_topic provided by the user.
    """
    gemini_client = get_gemini_client()
    nodes = []
    edges = []

    # A single, comprehensive prompt to generate the entire graph structure
    # for the specific system topic provided by the user.
    prompt = f"""
    You are a systems engineering expert. For the system topic "{system_topic}", generate a complete, hierarchical data structure as a single JSON object.

    The JSON object must have four keys: "srs", "sds", "vrs", and "vms".
    - "srs": A list of 3 system requirement strings.
    - "sds": A list of 7 system design strings.
    - "vrs": A list of 12 verification requirement strings.
    - "vms": A list of 20 verification method strings.

    Ensure the content of each string is specific and relevant to the "{system_topic}".

    Example for "drone delivery system":
    {{
      "srs": ["Payload capacity > 5kg", "Operational range > 10km", "Real-time video feed"],
      "sds": ["Carbon fiber quadcopter frame", "High-capacity LiPo battery", "5.8GHz video transmitter", "GPS module", "Failsafe return-to-home logic", "Automated winch system", "Obstacle avoidance sensors"],
      "vrs": ["Structural load test", "Battery discharge cycle test", "Video signal range check", "GPS signal lock time", "Return-to-home activation test", "Winch deployment speed test", ...],
      "vms": ["Apply 10kg static load to frame for 60s", "Measure flight time from 100% to 10% battery", "Record video quality at 10km distance", "Time to acquire 8+ satellite locks from cold start", ...]
    }}

    Generate the JSON now for the system: "{system_topic}".
    """

    try:
        # Generate all content in one atomic call
        response = gemini_client.generate_content(prompt)
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        graph_data = json.loads(json_str)

        srs = graph_data.get("srs", [])
        sds = graph_data.get("sds", [])
        vrs = graph_data.get("vrs", [])
        vms = graph_data.get("vms", [])

        def truncate_label(text, word_limit=6):
            """Shortens text to a specific number of words for display."""
            words = text.split()
            if len(words) > word_limit:
                return ' '.join(words[:word_limit]) + '...'
            return text

        # --- Graph Construction ---
        
        root_node = {"id": "system_topic", "label": system_topic, "group": "System", "level": 0, "title": system_topic, "font": {"size": 18}}
        nodes.append(root_node)

        sr_nodes = [{"id": f"SR-{i}", "label": truncate_label(label), "group": "System Requirement", "level": 1, "title": label, "shape": "box", "widthConstraint": {"maximum": 200}} for i, label in enumerate(srs)]
        nodes.extend(sr_nodes)
        for sr_node in sr_nodes:
            edges.append({"from": root_node["id"], "to": sr_node["id"], "arrows": "to"})

        sd_nodes = [{"id": f"SD-{i}", "label": truncate_label(label), "group": "System Design", "level": 2, "title": label, "shape": "box", "widthConstraint": {"maximum": 200}} for i, label in enumerate(sds)]
        nodes.extend(sd_nodes)
        if sr_nodes:
            for sd_node in sd_nodes:
                edges.append({"from": random.choice(sr_nodes)["id"], "to": sd_node["id"], "arrows": "to"})

        vr_nodes = [{"id": f"VR-{i}", "label": truncate_label(label), "group": "Verification Requirement", "level": 3, "title": label, "shape": "box", "widthConstraint": {"maximum": 200}} for i, label in enumerate(vrs)]
        nodes.extend(vr_nodes)
        if sd_nodes:
            for vr_node in vr_nodes:
                edges.append({"from": random.choice(sd_nodes)["id"], "to": vr_node["id"], "arrows": "to"})

        vm_nodes = [{"id": f"VM-{i}", "label": truncate_label(label), "group": "Verification Method", "level": 4, "title": label, "shape": "box", "widthConstraint": {"maximum": 200}} for i, label in enumerate(vms)]
        nodes.extend(vm_nodes)
        if vr_nodes:
            for vm_node in vm_nodes:
                # Ensure there's a parent to connect to
                if vr_nodes:
                    edges.append({"from": random.choice(vr_nodes)["id"], "to": vm_node["id"], "arrows": "to"})
        elif sd_nodes: # Fallback if no VRs
             for vm_node in vm_nodes:
                if sd_nodes:
                    edges.append({"from": random.choice(sd_nodes)["id"], "to": vm_node["id"], "arrows": "to", "dashes": True})
        elif sr_nodes: # Fallback if no SDs
            for vm_node in vm_nodes:
                if sr_nodes:
                    edges.append({"from": random.choice(sr_nodes)["id"], "to": vm_node["id"], "arrows": "to", "dashes": True})

    except (Exception, json.JSONDecodeError) as e:
        print(f"FATAL: Could not generate or parse the monolithic graph data. Error: {e}")
        return {
            "nodes": [{"id": "error", "label": "Error Generating Graph", "title": str(e), "level": 0}],
            "edges": []
        }

    return {"nodes": nodes, "edges": edges}
