from typing import Dict, Any


def get_hardcoded_isomorphism_graph_data() -> Dict[str, Any]:
    """
    Hardcoded, ASCII-safe isomorphism graph for the mechanical spring-mass-damper
    system and the electrical series RLC circuit. This provides a deterministic
    fallback when graph generation is requested via the hard-rule path.
    """
    nodes = [
        # Mechanical (left)
        {"id": "A1", "name": "Input", "type": "Input", "math": "F(t)", "meaning": "Applied force", "system": "mechanical"},
        {"id": "A2", "name": "Output", "type": "Output", "math": "x(t)", "meaning": "Displacement", "system": "mechanical"},
        {"id": "A3", "name": "Output", "type": "Output", "math": "v(t)", "meaning": "Velocity dx/dt", "system": "mechanical"},
        {"id": "A4", "name": "State Update", "type": "State Function", "math": "S=[x,v]; Sdot=[v, (1/m)(F - c v - k x)]", "meaning": "Second-order ODE in state-space form", "system": "mechanical"},
        {"id": "A5", "name": "Transfer Fn", "type": "Transfer Function", "math": "X(s)/F(s)=1/(m s^2 + c s + k)", "meaning": "Mechanical transfer function", "system": "mechanical"},
        {"id": "A6", "name": "Input Interface", "type": "Interface", "math": "F(t) -> state", "meaning": "Effort input to states", "system": "mechanical"},
        {"id": "A7", "name": "Output Interface", "type": "Interface", "math": "state -> {x,v}", "meaning": "Project states to outputs", "system": "mechanical"},

        # Electrical (right)
        {"id": "B1", "name": "Input", "type": "Input", "math": "E(t)", "meaning": "Applied voltage", "system": "electrical"},
        {"id": "B2", "name": "Output", "type": "Output", "math": "q(t)", "meaning": "Charge", "system": "electrical"},
        {"id": "B3", "name": "Output", "type": "Output", "math": "i(t)", "meaning": "Current dq/dt", "system": "electrical"},
        {"id": "B4", "name": "State Update", "type": "State Function", "math": "S=[q,i]; Sdot=[i, (1/L)(E - R i - (1/C) q)]", "meaning": "Second-order ODE in state-space form", "system": "electrical"},
        {"id": "B5", "name": "Transfer Fn", "type": "Transfer Function", "math": "Q(s)/E(s)=1/(L s^2 + R s + 1/C)", "meaning": "Electrical transfer function", "system": "electrical"},
        {"id": "B6", "name": "Input Interface", "type": "Interface", "math": "E(t) -> state", "meaning": "Effort input to states", "system": "electrical"},
        {"id": "B7", "name": "Output Interface", "type": "Interface", "math": "state -> {q,i}", "meaning": "Project states to outputs", "system": "electrical"},
    ]

    arcs = [
        {"source": "A1", "target": "B1", "weight": 0.95, "justification": "Force and voltage are effort inputs driving identical second-order dynamics."},
        {"source": "A2", "target": "B2", "weight": 0.90, "justification": "Displacement x and charge q are generalized coordinates storing potential energy."},
        {"source": "A3", "target": "B3", "weight": 0.90, "justification": "Velocity dx/dt and current dq/dt are flow variables (derivatives of the generalized coordinate)."},
        {"source": "A4", "target": "B4", "weight": 0.97, "justification": "State-space updates are structurally identical under m<->L, c<->R, k<->1/C."},
        {"source": "A5", "target": "B5", "weight": 0.98, "justification": "Transfer functions share the same canonical second-order form with mapped coefficients."},
        {"source": "A6", "target": "B6", "weight": 0.85, "justification": "Single effort input coupling into the state vector in both systems."},
        {"source": "A7", "target": "B7", "weight": 0.88, "justification": "Outputs are linear projections of the state vector in both systems."},
    ]

    explanation = (
        "This diagram shows the structural isomorphism between the mechanical spring-mass-damper "
        "system and the electrical series RLC circuit. Coefficient mapping m<->L, c<->R, k<->1/C "
        "makes their second-order ODEs and transfer functions identical in form. Nodes represent "
        "inputs, outputs, state updates, transfer functions, and interfaces. Arc weights reflect "
        "the strength of each correspondence."
    )

    return {
        "nodes": nodes,
        "arcs": arcs,
        "explanation": explanation,
        "system1_name": "Mechanical Spring-Mass-Damper",
        "system2_name": "Electrical RLC Circuit",
    }
