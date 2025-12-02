import json
from typing import List, Dict, Any
from .morphism_detector import Morphism


class JustificationGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_full_justification(self, system1, system2, morphisms: List[Morphism]) -> str:
        sections = [
            self._executive_summary(system1, system2, morphisms),
            self._system_specifications(system1, system2),
            self._morphism_analysis_details(morphisms),
            self._parameter_correspondence(morphisms),
            self._conclusions_and_implications(morphisms)
        ]

        return "\n\n".join(sections)

    def _executive_summary(self, s1, s2, morphisms: List[Morphism]) -> str:
        iso_count = sum(1 for m in morphisms if m.morphism_type == "ISOMORPHIC")
        homo_count = sum(1 for m in morphisms if m.morphism_type == "HOMOMORPHIC")
        avg_strength = sum(m.strength for m in morphisms) / len(morphisms) if morphisms else 0

        prompt = f"""
Generate a concise executive summary (150-200 words) for:

Comparing: {s1.system_name} vs {s2.system_name}

Key findings:
- {iso_count} isomorphic morphisms found
- {homo_count} homomorphic morphisms found
- Average strength: {avg_strength:.1%}

Emphasize: Overall system equivalence, key differences, practical implications
Use technical but accessible language.
"""

        success, response = self.llm.generate_content(prompt)
        return response if success else f"## EXECUTIVE SUMMARY\n\nComparing {s1.system_name} and {s2.system_name}: {iso_count} isomorphisms, {homo_count} homomorphisms detected."

    def _system_specifications(self, s1, s2) -> str:
        # Helper to safely get component attribute or 'N/A'
        def get_comp_attr(component_spec, attr_name):
            return getattr(component_spec, attr_name, 'N/A')

        return f"""## SYSTEM SPECIFICATIONS

### System 1: {s1.system_name}
- **Input**: {get_comp_attr(s1.input, 'symbol')} ({get_comp_attr(s1.input, 'units')})
- **Output**: {get_comp_attr(s1.output, 'symbol')} ({get_comp_attr(s1.output, 'units')})
- **State Dimension**: {get_comp_attr(s1.state_variables, 'dimension')}
- **Type**: {get_comp_attr(s1.next_state_function, 'system_type')}
- **Order**: {get_comp_attr(s1.next_state_function, 'order')}

### System 2: {s2.system_name}
- **Input**: {get_comp_attr(s2.input, 'symbol')} ({get_comp_attr(s2.input, 'units')})
- **Output**: {get_comp_attr(s2.output, 'symbol')} ({get_comp_attr(s2.output, 'units')})
- **State Dimension**: {get_comp_attr(s2.state_variables, 'dimension')}
- **Type**: {get_comp_attr(s2.next_state_function, 'system_type')}
- **Order**: {get_comp_attr(s2.next_state_function, 'order')}
"""

    def _morphism_analysis_details(self, morphisms: List[Morphism]) -> str:
        sections = ["# DETAILED MORPHISM ANALYSIS\n"]

        morphism_labels = {
            "M_Input": "Input Morphism",
            "M_Output": "Output Morphism",
            "M_State": "State Vector Morphism",
            "M_StateTrans": "State Transition Function Morphism",
            "M_TransferFunc": "Transfer Function Morphism",
            "M_Interface": "Interface Morphism"
        }

        for idx, morphism in enumerate(morphisms, 1):
            label = morphism_labels.get(morphism.id, f"Morphism {idx}")
            sections.append(f"## {idx}. {label}")
            sections.append(f"**Source**: {morphism.source}")
            sections.append(f"**Target**: {morphism.target}")
            sections.append(f"**Type**: {morphism.morphism_type}")
            sections.append(f"**Strength**: {morphism.strength:.2f} ({morphism.strength*100:.1f}%)")

            sections.append(f"\n{morphism.justification}")

            if morphism.analysis_points:
                sections.append("\n**Structural Analysis:**")
                for point in morphism.analysis_points:
                    sections.append(f"- {point}")

            if morphism.parameter_map:
                sections.append("\n**Parameter Correspondence:**")
                for k, v in morphism.parameter_map.items():
                    sections.append(f"- {k} ↔ {v}")

            if morphism.information_loss:
                sections.append(f"\n**Information Loss**: {morphism.information_loss}")

        return "\n".join(sections)

    def _parameter_correspondence(self, morphisms: List[Morphism]) -> str:
        sections = ["# PARAMETER CORRESPONDENCE GUIDE\n"]
        sections.append("If you want to transform a controller or model from System 1 to System 2, use these parameter substitutions:\n")

        all_params = {}
        for morphism in morphisms:
            if morphism.parameter_map:
                all_params.update(morphism.parameter_map)

        if all_params:
            sections.append("| System 1 | ↔ | System 2 |")
            sections.append("|----------|---|----------|")
            for k, v in all_params.items():
                sections.append(f"| {k} | ↔ | {v} |")
        else:
            sections.append("No direct parameter correspondences identified.")

        return "\n".join(sections)

    def _conclusions_and_implications(self, morphisms: List[Morphism]) -> str:
        iso_count = sum(1 for m in morphisms if m.morphism_type == "ISOMORPHIC")
        total = len(morphisms)
        isomorphic_pct = iso_count / total * 100 if total > 0 else 0
        avg_strength = sum(m.strength for m in morphisms) / total if total > 0 else 0

        prompt = f"""
Generate conclusions and practical implications (200-300 words) based on:

- {iso_count} out of {total} morphisms are isomorphic ({isomorphic_pct:.0f}%)
- Overall system similarity: {avg_strength:.1%}

Address:
1. System equivalence level
2. Can controllers/designs transfer between systems?
3. What must be adapted vs what transfers directly?
4. Validation considerations
5. Potential for unified analysis framework
"""

        success, response = self.llm.generate_content(prompt)
        if success:
            return f"# CONCLUSIONS AND IMPLICATIONS\n\n{response}"
        else:
            return f"""# CONCLUSIONS AND IMPLICATIONS

These systems show {avg_strength:.1%} overall equivalence with {isomorphic_pct:.0f}% perfect isomorphisms.
Controllers designed for one system can be partially transferred to the other with appropriate parameter substitution."""
