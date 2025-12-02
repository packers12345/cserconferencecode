from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Dict, List, Tuple

from Systems_Engineering_Chatbot.src.morphism_detector import Morphism
from Systems_Engineering_Chatbot.src.system_component_extractor import ExtractedSystemSpec, ComponentSpec


@dataclass
class _Node:
    node_id: str
    label: str
    detail: str
    system: str
    x: float = 0
    y: float = 0


class IsomorphismGraphRenderer:
    """
    Lightweight SVG renderer for isomorphism graphs.
    Two entry points are supported:
      - render_static_isomorphism_graph_svg: render deterministic, hardcoded graph data.
      - render_full_visualization: render dynamic data from ExtractedSystemSpec + Morphism objects.
    """

    def __init__(self, width: int = 1200, height: int = 850):
        self.width = width
        self.height = height
        self.node_width = 160
        self.node_height = 90
        self.left_margin = 80
        self.right_margin = 80
        self.vertical_spacing = 110

    # ------------------------------------------------------------------ #
    # Public entry points
    # ------------------------------------------------------------------ #
    def render_static_isomorphism_graph_svg(
        self,
        nodes_data: List[Dict],
        arcs_data: List[Dict],
        explanation_text: str,
        system1_name: str,
        system2_name: str,
    ) -> str:
        mech_nodes = [n for n in nodes_data if n.get("system") == "mechanical"]
        elec_nodes = [n for n in nodes_data if n.get("system") == "electrical"]

        mech_nodes_built = [
            _Node(node_id=n["id"], label=n["name"], detail=n.get("math", ""), system="mechanical")
            for n in mech_nodes
        ]
        elec_nodes_built = [
            _Node(node_id=n["id"], label=n["name"], detail=n.get("math", ""), system="electrical")
            for n in elec_nodes
        ]

        mech_nodes_built = self._assign_positions(mech_nodes_built, x=self.left_margin, start_y=80)
        elec_nodes_built = self._assign_positions(
            elec_nodes_built,
            x=self.width - self.right_margin - self.node_width,
            start_y=80,
        )

        node_lookup = {n.node_id: n for n in mech_nodes_built + elec_nodes_built}
        return self._render_svg(
            mech_nodes_built + elec_nodes_built,
            arcs_data,
            explanation_text,
            system1_name,
            system2_name,
            node_lookup=node_lookup,
        )

    def render_full_visualization(
        self,
        system1: ExtractedSystemSpec,
        system2: ExtractedSystemSpec,
        morphisms: List[Morphism],
    ) -> str:
        sys1_nodes = self._build_nodes_from_spec(system1, prefix="A", system_label="System 1")
        sys2_nodes = self._build_nodes_from_spec(system2, prefix="B", system_label="System 2")

        sys1_nodes = self._assign_positions(sys1_nodes, x=self.left_margin, start_y=80)
        sys2_nodes = self._assign_positions(
            sys2_nodes,
            x=self.width - self.right_margin - self.node_width,
            start_y=80,
        )

        node_lookup = {n.node_id: n for n in sys1_nodes + sys2_nodes}
        arcs_data = []
        for m in morphisms:
            if m.source not in node_lookup or m.target not in node_lookup:
                continue
            arcs_data.append(
                {
                    "source": m.source,
                    "target": m.target,
                    "weight": self._to_float(m.strength),
                    "justification": m.justification or "",
                }
            )

        explanation = (
            f"Detected {len(arcs_data)} morphisms between {system1.system_name} and {system2.system_name}. "
            "Edges are weighted by morphism strength."
        )

        return self._render_svg(
            sys1_nodes + sys2_nodes,
            arcs_data,
            explanation,
            system1.system_name,
            system2.system_name,
            node_lookup=node_lookup,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _assign_positions(self, nodes: List[_Node], x: float, start_y: float) -> List[_Node]:
        for idx, node in enumerate(nodes):
            node.x = x
            node.y = start_y + idx * self.vertical_spacing
        return nodes

    def _build_nodes_from_spec(self, spec: ExtractedSystemSpec, prefix: str, system_label: str) -> List[_Node]:
        components: List[Tuple[str, ComponentSpec]] = [
            ("input", spec.input),
            ("output", spec.output),
            ("state", spec.state_variables),
            ("next_state", spec.next_state_function),
            ("transfer_fn", spec.transfer_function),
            ("interface", spec.interface),
        ]

        nodes: List[_Node] = []
        for idx, (name, comp) in enumerate(components, 1):
            label = comp.symbol or name
            detail_parts = [
                part
                for part in [
                    getattr(comp, "equation", None),
                    getattr(comp, "vector_form", None),
                    getattr(comp, "symbolic_form", None),
                ]
                if part and part != "N/A"
            ]
            detail = detail_parts[0] if detail_parts else comp.description or ""
            nodes.append(
                _Node(
                    node_id=f"{prefix}{idx}",
                    label=label,
                    detail=detail,
                    system=system_label,
                )
            )
        return nodes

    def _render_svg(
        self,
        nodes: List[_Node],
        arcs: List[Dict],
        explanation: str,
        system1_name: str,
        system2_name: str,
        node_lookup: Dict[str, _Node],
    ) -> str:
        output = StringIO()
        output.write(f'<svg width="{self.width}" height="{self.height}" ')
        output.write(f'viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">\n')
        output.write("<defs>\n")
        output.write(self._styles())
        output.write(self._markers())
        output.write("</defs>\n")
        output.write(f'<rect width="{self.width}" height="{self.height}" fill="#f9fafb"/>\n')
        output.write(self._title(system1_name, system2_name))
        output.write(self._render_nodes(nodes))
        output.write(self._render_arcs(arcs, node_lookup))
        output.write(self._explanation(explanation))
        output.write("</svg>")
        return output.getvalue()

    def _styles(self) -> str:
        return """
        <style>
            .node-box { rx: 8; stroke-width: 2; }
            .node-label { font-size: 11px; font-weight: bold; fill: #1f2937; }
            .node-detail { font-size: 9px; fill: #4b5563; }
            .arc { stroke: #1f2937; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
            .arc-label { font-size: 9px; fill: #111827; }
            .title { font-size: 18px; font-weight: bold; fill: #111827; }
        </style>
        """

    def _markers(self) -> str:
        return """
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#111827"/>
        </marker>
        """

    def _title(self, sys1: str, sys2: str) -> str:
        return f"""
        <g class="title-section">
            <text x="{self.width/2}" y="30" class="title" text-anchor="middle">
                Isomorphism Analysis: {sys1} <-> {sys2}
            </text>
        </g>
        """

    def _render_nodes(self, nodes: List[_Node]) -> str:
        output = StringIO()
        for node in nodes:
            output.write(f"""
            <g class="node" id="{node.node_id}">
                <rect class="node-box" x="{node.x}" y="{node.y}" width="{self.node_width}" height="{self.node_height}"
                      fill="#e0f2fe" stroke="#2563eb"/>
                <text class="node-label" x="{node.x + 10}" y="{node.y + 20}">{node.label}</text>
                <text class="node-detail" x="{node.x + 10}" y="{node.y + 38}">{self._escape(node.detail)[:60]}</text>
                <text class="node-detail" x="{node.x + 10}" y="{node.y + 56}">{node.system}</text>
            </g>
            """)
        return output.getvalue()

    def _render_arcs(self, arcs: List[Dict], node_lookup: Dict[str, _Node]) -> str:
        output = StringIO()
        for idx, arc in enumerate(arcs, 1):
            src = node_lookup.get(arc.get("source"))
            tgt = node_lookup.get(arc.get("target"))
            if not src or not tgt:
                continue
            x1 = src.x + self.node_width
            y1 = src.y + self.node_height / 2
            x2 = tgt.x
            y2 = tgt.y + self.node_height / 2
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2 - 6
            justification = self._escape(arc.get("justification", ""))
            output.write(f"""
            <g class="arc">
                <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="arc" />
                <text class="arc-label" x="{label_x}" y="{label_y}">w={arc.get('weight', 0):.2f}</text>
                <text class="arc-label" x="{label_x}" y="{label_y + 14}">{justification[:80]}</text>
            </g>
            """)
        return output.getvalue()

    def _explanation(self, text: str) -> str:
        return f"""
        <g class="explanation">
            <text x="40" y="{self.height - 80}" font-size="12" font-weight="bold" fill="#111827">Explanation</text>
            <text x="40" y="{self.height - 60}" font-size="11" fill="#374151">{self._escape(text)[:240]}</text>
        </g>
        """

    @staticmethod
    def _escape(value: str) -> str:
        return (value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _to_float(value) -> float:
        try:
            return float(value)
        except Exception:
            return 0.5
