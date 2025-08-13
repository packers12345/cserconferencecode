# -*- coding: utf-8 -*-
"""
Systems Diagram Generator for Wymorian Systems Engineering Chatbot.

This module provides functions to convert the structured conversation data,
containing Wymorian artifacts, into a graph format suitable for visualization
with libraries like vis.js.
"""

def create_system_diagram(artifacts: list, system_topic: str) -> dict:
    """
    Generates a vis.js-compatible graph from a list of structured artifacts.
    """
    nodes = []
    edges = []
    node_ids = set()

    # Add the central system topic node
    if "system_topic" not in node_ids:
        nodes.append({
            "id": "system_topic",
            "label": system_topic,
            "group": "System",
            "shape": "ellipse",
            "level": 0
        })
        node_ids.add("system_topic")

    # Create a dictionary to hold artifacts by type
    artifacts_by_type = {
        "SR": [],
        "SD": [],
        "VR": [],
        "VM": []
    }

    for artifact in artifacts:
        artifact_type = artifact.get("type")
        if artifact_type in artifacts_by_type:
            artifacts_by_type[artifact_type].append(artifact)

    # Process SRs
    for sr in artifacts_by_type["SR"]:
        sr_id = sr.get("id")
        if sr_id not in node_ids:
            nodes.append({
                "id": sr_id,
                "label": f"{sr_id}: System Requirement",
                "group": "System Requirement",
                "level": 1
            })
            node_ids.add(sr_id)
        edges.append({"from": "system_topic", "to": sr_id, "label": "has requirement"})

    # Process SDs
    for sd in artifacts_by_type["SD"]:
        sd_id = sd.get("id")
        if sd_id not in node_ids:
            nodes.append({
                "id": sd_id,
                "label": f"{sd_id}: System Design",
                "group": "System Design",
                "level": 1
            })
            node_ids.add(sd_id)
        edges.append({"from": "system_topic", "to": sd_id, "label": "has design"})
        # Link SD to all SRs
        for sr in artifacts_by_type["SR"]:
            edges.append({"from": sd_id, "to": sr.get("id"), "label": "adheres to"})

    # Process VRs
    for vr in artifacts_by_type["VR"]:
        vr_id = vr.get("id")
        if vr_id not in node_ids:
            nodes.append({
                "id": vr_id,
                "label": f"{vr_id}: Verification Requirement",
                "group": "Verification Requirement",
                "level": 2
            })
            node_ids.add(vr_id)
        # Link VR to all SRs
        for sr in artifacts_by_type["SR"]:
            edges.append({"from": vr_id, "to": sr.get("id"), "label": "verifies"})

    # Process VMs
    for vm in artifacts_by_type["VM"]:
        vm_id = vm.get("id")
        if vm_id not in node_ids:
            nodes.append({
                "id": vm_id,
                "label": f"{vm_id}: Verification Method",
                "group": "Verification Method",
                "level": 3
            })
            node_ids.add(vm_id)
        # Link VM to all VRs
        for vr in artifacts_by_type["VR"]:
            edges.append({"from": vm_id, "to": vr.get("id"), "label": "satisfies"})

    return {"nodes": nodes, "edges": edges}
