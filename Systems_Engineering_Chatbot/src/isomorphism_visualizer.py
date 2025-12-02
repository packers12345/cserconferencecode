"""
Isomorphism Visualizer Module

Handles extraction, validation, and organization of isomorphism data from LLM analysis.
Produces structured graph data and text analysis reports for visualization.
"""

import json
from typing import Dict, Any, Optional, Tuple
import logging
from Systems_Engineering_Chatbot.src.prompts import get_isomorphism_extraction_prompt

logger = logging.getLogger(__name__)


class IsomorphismVisualizerError(Exception):
    """Base exception for isomorphism visualization errors."""
    pass


class IsomorphismExtractor:
    """Extracts isomorphism structure from LLM analysis output."""

    @staticmethod
    def validate_json_structure(data: Dict[str, Any]) -> bool:
        """
        Validates that extracted JSON matches the isomorphism graph schema.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            True if valid, raises IsomorphismVisualizerError otherwise
        """
        required_top_level = ["systems", "morphisms", "overall_assessment"]
        if not all(key in data for key in required_top_level):
            raise IsomorphismVisualizerError(
                f"JSON missing required top-level keys. Required: {required_top_level}"
            )

        # Validate systems array
        if not isinstance(data.get("systems"), list):
            raise IsomorphismVisualizerError("'systems' must be a list")
        
        if len(data["systems"]) != 2:
            raise IsomorphismVisualizerError("Exactly 2 systems required")

        for idx, system in enumerate(data["systems"]):
            required_system_keys = ["system_id", "system_name", "nodes"]
            if not all(key in system for key in required_system_keys):
                raise IsomorphismVisualizerError(
                    f"System {idx} missing required keys: {required_system_keys}"
                )

            if not isinstance(system.get("nodes"), list):
                raise IsomorphismVisualizerError(f"System {idx} 'nodes' must be a list")

            if len(system["nodes"]) < 5:
                logger.warning(
                    f"System {idx} has {len(system['nodes'])} nodes; expected ~5 component types"
                )

            for node_idx, node in enumerate(system["nodes"]):
                required_node_keys = ["node_id", "node_type", "label", "mathematical_form", "position"]
                if not all(key in node for key in required_node_keys):
                    raise IsomorphismVisualizerError(
                        f"System {idx}, Node {node_idx} missing required keys: {required_node_keys}"
                    )

                if not isinstance(node["position"], dict) or "x" not in node["position"] or "y" not in node["position"]:
                    raise IsomorphismVisualizerError(
                        f"System {idx}, Node {node_idx} position invalid; must have 'x' and 'y'"
                    )

        # Validate morphisms array
        if not isinstance(data.get("morphisms"), list):
            raise IsomorphismVisualizerError("'morphisms' must be a list")

        for morph_idx, morphism in enumerate(data["morphisms"]):
            required_morph_keys = ["morphism_id", "from_node", "to_node", "morphism_type", "confidence", "reasoning"]
            if not all(key in morphism for key in required_morph_keys):
                raise IsomorphismVisualizerError(
                    f"Morphism {morph_idx} missing required keys: {required_morph_keys}"
                )

            confidence = morphism.get("confidence")
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                raise IsomorphismVisualizerError(
                    f"Morphism {morph_idx} confidence must be a number between 0.0 and 1.0, got {confidence}"
                )

        # Validate overall_assessment
        if not isinstance(data.get("overall_assessment"), dict):
            raise IsomorphismVisualizerError("'overall_assessment' must be a dictionary")

        return True

    @staticmethod
    def extract_from_llm_response(llm_response: str) -> Dict[str, Any]:
        """
        Extracts and validates isomorphism JSON from LLM response.
        
        Args:
            llm_response: Raw LLM response (may contain JSON plus other text)
            
        Returns:
            Validated isomorphism graph dictionary
            
        Raises:
            IsomorphismVisualizerError: If JSON is invalid or malformed
        """
        # Try to extract JSON from response
        try:
            # First attempt: parse entire response as JSON
            data = json.loads(llm_response)
        except json.JSONDecodeError:
            # Second attempt: find JSON block in response
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                raise IsomorphismVisualizerError(
                    "No JSON found in LLM response. Response must contain valid isomorphism graph JSON."
                )
            
            try:
                data = json.loads(llm_response[json_start:json_end])
            except json.JSONDecodeError as e:
                raise IsomorphismVisualizerError(f"Failed to parse JSON from LLM response: {str(e)}")

        # Validate structure
        IsomorphismExtractor.validate_json_structure(data)
        
        return data


class IsomorphismAnalyzer:
    """Analyzes isomorphism data and generates text reports."""

    @staticmethod
    def generate_analysis_report(graph_data: Dict[str, Any]) -> str:
        """
        Generates a text analysis report from isomorphism graph data.
        
        Args:
            graph_data: Validated isomorphism graph dictionary
            
        Returns:
            Formatted text report explaining morphisms and isomorphism assessment
        """
        report_lines = []
        
        systems = graph_data.get("systems", [])
        morphisms = graph_data.get("morphisms", [])
        assessment = graph_data.get("overall_assessment", {})
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("ISOMORPHISM ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # System summaries
        report_lines.append("SYSTEMS ANALYZED:")
        for system in systems:
            system_name = system.get("system_name", "Unknown")
            node_count = len(system.get("nodes", []))
            report_lines.append(f"  - {system_name} ({node_count} components)")
        report_lines.append("")
        
        # Component details
        report_lines.append("COMPONENT MAPPING:")
        for system in systems:
            system_name = system.get("system_name", "Unknown")
            nodes = system.get("nodes", [])
            report_lines.append(f"\n  {system_name} Components:")
            for node in nodes:
                node_type = node.get("node_type", "unknown")
                label = node.get("label", "Unknown")
                math_form = node.get("mathematical_form", "N/A")
                report_lines.append(f"    - [{node_type.upper()}] {label}")
                report_lines.append(f"      {math_form}")
        report_lines.append("")
        
        # Morphism analysis
        report_lines.append("MORPHISM ANALYSIS:")
        report_lines.append("")
        
        high_conf_section = []
        medium_conf_section = []
        low_conf_section = []
        
        for morph in morphisms:
            confidence = morph.get("confidence", 0)
            from_node = morph.get("from_node", "?")
            to_node = morph.get("to_node", "?")
            morph_type = morph.get("morphism_type", "unknown")
            reasoning = morph.get("reasoning", "No reasoning provided")
            
            if confidence >= 0.8:
                high_conf_section.append((from_node, to_node, morph_type, confidence, reasoning, "[HI]"))
            elif confidence >= 0.5:
                medium_conf_section.append((from_node, to_node, morph_type, confidence, reasoning, "[MED]"))
            else:
                low_conf_section.append((from_node, to_node, morph_type, confidence, reasoning, "[LOW]"))
        
        if high_conf_section:
            report_lines.append("  High Confidence Morphisms (>=0.8):")
            for from_node, to_node, morph_type, confidence, reasoning, symbol in high_conf_section:
                report_lines.append(f"    {symbol} {from_node} <-> {to_node} [{morph_type}] ({confidence:.0%})")
                report_lines.append(f"      {reasoning}")
            report_lines.append("")
        
        if medium_conf_section:
            report_lines.append("  Medium Confidence Morphisms (0.5-0.8):")
            for from_node, to_node, morph_type, confidence, reasoning, symbol in medium_conf_section:
                report_lines.append(f"    {symbol} {from_node} <-> {to_node} [{morph_type}] ({confidence:.0%})")
                report_lines.append(f"      {reasoning}")
            report_lines.append("")
        
        if low_conf_section:
            report_lines.append("  Low Confidence Morphisms (<0.5):")
            for from_node, to_node, morph_type, confidence, reasoning, symbol in low_conf_section:
                report_lines.append(f"    {symbol} {from_node} <-> {to_node} [{morph_type}] ({confidence:.0%})")
                report_lines.append(f"      {reasoning}")
            report_lines.append("")
        
        # Overall assessment
        report_lines.append("OVERALL ASSESSMENT:")
        is_isomorphic = assessment.get("is_isomorphic", False)
        iso_type = assessment.get("isomorphism_type", "unknown")
        summary = assessment.get("summary", "No summary provided")
        
        report_lines.append(f"  Isomorphic: {'YES' if is_isomorphic else 'NO'}")
        report_lines.append(f"  Type: {iso_type}")
        report_lines.append(f"  Summary: {summary}")
        report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

    @staticmethod
    def compute_morphism_statistics(graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes statistics about the morphism structure.
        
        Args:
            graph_data: Validated isomorphism graph dictionary
            
        Returns:
            Dictionary with statistics (total morphisms, confidence distribution, types, etc.)
        """
        morphisms = graph_data.get("morphisms", [])
        
        if not morphisms:
            return {
                "total_morphisms": 0,
                "average_confidence": 0.0,
                "morphism_types": {},
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0}
            }
        
        morphism_types = {}
        total_confidence = 0
        high_conf = medium_conf = low_conf = 0
        
        for morph in morphisms:
            morph_type = morph.get("morphism_type", "unknown")
            morphism_types[morph_type] = morphism_types.get(morph_type, 0) + 1
            
            confidence = morph.get("confidence", 0)
            total_confidence += confidence
            
            if confidence >= 0.8:
                high_conf += 1
            elif confidence >= 0.5:
                medium_conf += 1
            else:
                low_conf += 1
        
        return {
            "total_morphisms": len(morphisms),
            "average_confidence": total_confidence / len(morphisms) if morphisms else 0.0,
            "morphism_types": morphism_types,
            "confidence_distribution": {
                "high": high_conf,
                "medium": medium_conf,
                "low": low_conf
            }
        }


class IsomorphismVisualizer:
    """Main interface for isomorphism analysis and visualization."""

    def __init__(self, gemini_client):
        """
        Initializes the visualizer with an LLM client.
        
        Args:
            gemini_client: Instance of GeminiClient for LLM calls
        """
        self.gemini_client = gemini_client
        self.extractor = IsomorphismExtractor()
        self.analyzer = IsomorphismAnalyzer()

    def extract_isomorphism_structure(
        self, 
        system_1_description: str, 
        system_2_description: str
    ) -> Dict[str, Any]:
        """
        Analyzes two systems via LLM and extracts isomorphism structure.
        
        Args:
            system_1_description: Description of the first system
            system_2_description: Description of the second system
            
        Returns:
            Dictionary containing:
                - graph_data: Validated isomorphism graph JSON
                - analysis_report: Text analysis report
                - statistics: Morphism statistics
                
        Raises:
            IsomorphismVisualizerError: If extraction or validation fails
        """
        try:
            # Generate prompt
            prompt = get_isomorphism_extraction_prompt(
                system_1_description, 
                system_2_description
            )
            
            # Call LLM with json_mode for structured output
            logger.info("Calling LLM for isomorphism extraction...")
            success, llm_response = self.gemini_client.generate_content(
                prompt,
                json_mode=True
            )
            if not success:
                raise IsomorphismVisualizerError(f"LLM generation failed: {llm_response}")
            # Ensure we pass a JSON string into the extractor
            if isinstance(llm_response, dict):
                llm_response = json.dumps(llm_response)
            
            logger.info("Extracting and validating JSON from LLM response...")
            # Extract and validate JSON
            graph_data = self.extractor.extract_from_llm_response(llm_response)
            
            # Generate analysis report
            logger.info("Generating analysis report...")
            analysis_report = self.analyzer.generate_analysis_report(graph_data)
            
            # Compute statistics
            logger.info("Computing morphism statistics...")
            statistics = self.analyzer.compute_morphism_statistics(graph_data)
            
            return {
                "graph_data": graph_data,
                "analysis_report": analysis_report,
                "statistics": statistics
            }
            
        except IsomorphismVisualizerError as e:
            logger.error(f"Isomorphism extraction error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during isomorphism extraction: {str(e)}")
            raise IsomorphismVisualizerError(
                f"Failed to extract isomorphism structure: {str(e)}"
            )

    def get_visualization_data(
        self,
        system_1_description: str,
        system_2_description: str
    ) -> Tuple[Dict[str, Any], str]:
        """
        Extracts isomorphism structure and returns both graph and report.
        
        Args:
            system_1_description: Description of the first system
            system_2_description: Description of the second system
            
        Returns:
            Tuple of (graph_data_dict, analysis_report_string)
        """
        result = self.extract_isomorphism_structure(
            system_1_description,
            system_2_description
        )
        
        return (result["graph_data"], result["analysis_report"])
